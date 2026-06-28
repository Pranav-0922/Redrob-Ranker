#!/usr/bin/env python3
"""
rank.py — AI Candidate Ranking System for Redrob Hackathon
Ranks 100,000 candidate profiles for a Senior AI Engineer role.

Usage:
    python rank.py --candidates candidates.jsonl --out submission.csv

Author: Redrob Hackathon Submission
"""

import argparse
import csv
import gzip
import json
import math
import re
import time
from datetime import date, datetime
from pathlib import Path

from tqdm import tqdm

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────

MUST_HAVE_SKILLS = {
    "python", "embeddings", "vector search", "rag", "nlp", "retrieval",
    "sentence-transformers", "sentence transformers", "faiss", "pinecone",
    "qdrant", "milvus", "weaviate", "transformers", "fine-tuning", "fine tuning",
    "finetuning", "llm", "llms", "ranking", "ndcg", "a/b testing", "ab testing",
    "information retrieval", "semantic search", "huggingface", "hugging face",
    "langchain", "llamaindex", "llama index", "openai", "gpt", "bert", "retrieval augmented",
}

GOOD_TO_HAVE_SKILLS = {
    "lora", "qlora", "xgboost", "lightgbm", "spark", "kafka",
    "fastapi", "docker", "pytorch", "tensorflow", "mlflow", "kubeflow",
    "kubernetes", "redis", "elasticsearch", "opensearch", "dbt",
}

# CV/Speech/Robotics — primary expertise in these with no NLP = penalize
CV_SPEECH_SKILLS = {
    "computer vision", "image classification", "object detection", "ocr",
    "speech recognition", "tts", "text to speech", "speech synthesis",
    "robotics", "slam", "pose estimation", "image segmentation",
    "yolo", "resnet", "cnn", "convolutional", "mediapipe",
}

CONSULTING_FIRMS = {
    "tcs", "tata consultancy", "infosys", "wipro", "accenture", "cognizant",
    "capgemini", "hcl", "hcl technologies", "tech mahindra", "hexaware",
    "mphasis", "l&t infotech", "ltimindtree", "mindtree", "niit technologies",
    "patni", "mastech", "zensar", "cyient", "persistent systems",
    "mphasis bfl",
}

GOOD_LOCATIONS = {
    "pune", "noida", "delhi", "gurugram", "gurgaon", "hyderabad",
    "mumbai", "bangalore", "bengaluru", "ncr", "new delhi",
    "delhi ncr", "greater noida",
}

PRODUCTION_KEYWORDS = [
    "deployed", "production", "shipped", "real users", "scale", "built",
    "launched", "served", "system", "pipeline", "api", "millions",
    "traffic", "latency", "throughput", "microservice", "kubernetes",
    "docker", "monitoring", "alerting", "a/b test", "live", "online",
]

NON_TECH_TITLE_TOKENS = {
    "manager", "director", "vp", "vice president", "head", "lead",
    "hr", "human resources", "marketing", "sales", "operations",
    "recruiter", "talent", "finance", "legal", "admin", "coordinator",
}

TODAY = date.today()


# ─────────────────────────────────────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────────────────────────────────────

def load_candidates(path: str) -> list[dict]:
    """
    Load candidate records from a JSONL or gzipped JSONL file.
    Supports both .jsonl and .jsonl.gz extensions.
    Returns a list of candidate dicts.
    """
    p = Path(path)
    records = []

    open_fn = gzip.open if p.suffix == ".gz" else open
    mode = "rt"

    with open_fn(p, mode, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    pass  # skip malformed lines

    return records


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def normalize(s: str) -> str:
    """Lowercase and strip a string for consistent matching."""
    return s.lower().strip() if s else ""


def proficiency_weight(p: str) -> float:
    """Map proficiency level to a numeric weight."""
    return {"expert": 1.0, "advanced": 0.8, "intermediate": 0.5, "beginner": 0.2}.get(
        normalize(p), 0.3
    )


def days_since(date_str: str) -> int:
    """Return days between a date string (YYYY-MM-DD) and today."""
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d").date()
        return (TODAY - d).days
    except Exception:
        return 9999  # treat unknown as very old


# ─────────────────────────────────────────────────────────────────────────────
# HONEYPOT DETECTION
# ─────────────────────────────────────────────────────────────────────────────

def detect_honeypot(candidate: dict) -> bool:
    """
    Return True if the candidate looks like a synthetic trap / honeypot.
    Five checks — any single one being True flags the candidate.
    These are scored as 0 and excluded from the final top-100.
    """
    profile = candidate.get("profile", {})
    skills = candidate.get("skills", [])
    signals = candidate.get("redrob_signals", {})
    education = candidate.get("education", [])

    # Check 1: 10+ skills all "expert" with almost no endorsements — fake profile
    if len(skills) >= 10:
        expert_count = sum(1 for s in skills if normalize(s.get("proficiency", "")) == "expert")
        total_endorsements = sum(s.get("endorsements", 0) for s in skills)
        if expert_count >= 10 and total_endorsements < 10:
            return True

    # Check 2: Non-technical title but skills are 80%+ AI/ML keywords
    title = normalize(profile.get("current_title", ""))
    is_nontec_title = any(tok in title for tok in NON_TECH_TITLE_TOKENS)
    if is_nontec_title and skills:
        all_skill_names = {normalize(s.get("name", "")) for s in skills}
        ai_ml_terms = MUST_HAVE_SKILLS | GOOD_TO_HAVE_SKILLS
        ai_overlap = sum(
            1 for sk in all_skill_names
            if any(term in sk for term in ai_ml_terms)
        )
        if ai_overlap / len(all_skill_names) >= 0.8:
            return True

    # Check 3: open_to_work=True + last_active > 365 days + offer_acceptance=1.0
    # Real candidates fitting this combo perfectly are statistically implausible
    if signals.get("open_to_work_flag") is True:
        if days_since(signals.get("last_active_date", "")) > 365:
            if signals.get("offer_acceptance_rate", -1) == 1.0:
                return True

    # Check 4: years_of_experience > 15 but education end_year implies age < 25
    yoe = profile.get("years_of_experience", 0)
    if yoe > 15 and education:
        # Estimate graduation year from most recent education
        end_years = [e.get("end_year", 0) for e in education if e.get("end_year")]
        if end_years:
            latest_grad = max(end_years)
            # If they graduated ≤4 years ago, 15+ YOE is impossible
            years_since_grad = TODAY.year - latest_grad
            if years_since_grad <= 4:
                return True

    # Check 5: All skills have duration_months=0 but proficiency=expert
    if skills and len(skills) >= 3:
        all_zero_duration = all(s.get("duration_months", 0) == 0 for s in skills)
        all_expert = all(normalize(s.get("proficiency", "")) == "expert" for s in skills)
        if all_zero_duration and all_expert:
            return True

    return False


# ─────────────────────────────────────────────────────────────────────────────
# COMPONENT 1: SKILLS SCORE (35%)
# ─────────────────────────────────────────────────────────────────────────────

def score_skills(candidate: dict) -> float:
    """
    Score based on how well the candidate's skills match must-have and good-to-have lists.
    Accounts for proficiency, endorsements, duration, and assessment scores.
    Returns a float in [0, 1].
    """
    skills = candidate.get("skills", [])
    signals = candidate.get("redrob_signals", {})
    assessment_scores = signals.get("skill_assessment_scores", {}) or {}

    if not skills:
        return 0.0

    must_have_score = 0.0
    good_to_have_score = 0.0
    cv_speech_count = 0
    nlp_retrieval_count = 0

    # Cap contributions to avoid one amazing skill dominating
    max_must = len(MUST_HAVE_SKILLS)
    max_good = len(GOOD_TO_HAVE_SKILLS)

    for skill in skills:
        name = normalize(skill.get("name", ""))
        prof_w = proficiency_weight(skill.get("proficiency", ""))
        endorsements = skill.get("endorsements", 0)
        duration = skill.get("duration_months", 0)

        # Endorsement bonus: logarithmic so 100 endorsements ≈ full bonus
        endorse_bonus = math.log(endorsements + 1) / math.log(100 + 1)

        # Duration bonus: caps at 3 years (36 months)
        duration_bonus = min(duration / 36.0, 1.0)

        # Composite skill quality weight
        skill_quality = prof_w * (1 + 0.3 * endorse_bonus + 0.2 * duration_bonus)

        # Assessment score bonus: rewarded if they've taken a test for this skill
        assess_bonus = 0.0
        for assess_key, assess_val in assessment_scores.items():
            if normalize(assess_key) in name or name in normalize(assess_key):
                assess_bonus = (assess_val / 100.0) * 0.2
                break

        final_skill_quality = skill_quality + assess_bonus

        # Check if this skill is a must-have
        matched_must = any(term in name or name in term for term in MUST_HAVE_SKILLS)
        matched_good = any(term in name or name in term for term in GOOD_TO_HAVE_SKILLS)
        matched_cv = any(term in name or name in term for term in CV_SPEECH_SKILLS)

        if matched_must:
            must_have_score += final_skill_quality
            nlp_retrieval_count += 1
        elif matched_good:
            good_to_have_score += final_skill_quality

        if matched_cv:
            cv_speech_count += 1

    # Normalize: express as fraction of "ideal" coverage
    # Ideal: all must-haves at expert = max_must * 1.0
    # We normalise to a 0-1 range
    must_norm = min(must_have_score / (max_must * 1.5), 1.0)
    good_norm = min(good_to_have_score / (max_good * 1.5), 1.0)

    combined = must_norm * 0.75 + good_norm * 0.25

    # Penalize if candidate's top skills are entirely CV/Speech with no NLP/retrieval
    if cv_speech_count > 0 and nlp_retrieval_count == 0:
        penalty = min(cv_speech_count / max(len(skills), 1), 0.6)
        combined *= (1.0 - penalty)

    return min(combined, 1.0)


# ─────────────────────────────────────────────────────────────────────────────
# COMPONENT 2: CAREER QUALITY SCORE (25%)
# ─────────────────────────────────────────────────────────────────────────────

def score_career(candidate: dict) -> float:
    """
    Score career quality: product vs consulting background, production signals,
    job stability, and current role relevance.
    Returns a float in [0, 1].
    """
    profile = candidate.get("profile", {})
    career = candidate.get("career_history", [])

    if not career:
        return 0.3  # unknown, give benefit of doubt

    # ── Consulting check ──
    def is_consulting(company: str) -> bool:
        cn = normalize(company)
        return any(firm in cn for firm in CONSULTING_FIRMS)

    all_consulting = all(is_consulting(job.get("company", "")) for job in career)
    current_consulting = is_consulting(profile.get("current_company", ""))
    has_product_history = any(
        not is_consulting(job.get("company", "")) for job in career
    )

    if all_consulting:
        # Career entirely in body-shopping firms — strong penalty
        base = 0.1
    elif current_consulting and has_product_history:
        # Currently at consulting but has product experience — moderate
        base = 0.5
    else:
        base = 0.75

    # ── Production signals in job descriptions ──
    all_descriptions = " ".join(
        normalize(job.get("description", "")) for job in career
    )
    production_hits = sum(1 for kw in PRODUCTION_KEYWORDS if kw in all_descriptions)
    # Max 8 hits for full bonus; each hit adds ~3%
    production_bonus = min(production_hits / 8.0, 1.0) * 0.25
    base = min(base + production_bonus, 1.0)

    # ── Job-hopping penalty ──
    # 3 or more roles each under 18 months is a red flag
    short_stints = sum(
        1 for job in career
        if job.get("duration_months", 999) < 18 and not job.get("is_current", False)
    )
    if short_stints >= 3:
        base *= 0.7  # 30% penalty

    # ── Non-technical current role penalty ──
    current_title = normalize(profile.get("current_title", ""))
    if any(tok in current_title for tok in NON_TECH_TITLE_TOKENS):
        base *= 0.5

    return min(base, 1.0)


# ─────────────────────────────────────────────────────────────────────────────
# COMPONENT 3: EXPERIENCE SCORE (20%)
# ─────────────────────────────────────────────────────────────────────────────

def score_experience(candidate: dict) -> float:
    """
    Score years of experience against the sweet spot for this role (6-8 years).
    Too junior or too senior both get lower scores.
    Returns a float in [0, 1].
    """
    years = candidate.get("profile", {}).get("years_of_experience", 0)

    if 6 <= years <= 8:
        return 1.0
    elif 5 <= years < 6 or 8 < years <= 9:
        return 0.85
    elif 4 <= years < 5 or 9 < years <= 11:
        return 0.65
    elif years < 4:
        return 0.3
    else:  # > 11
        return 0.5


# ─────────────────────────────────────────────────────────────────────────────
# COMPONENT 4: LOCATION & AVAILABILITY SCORE (10%)
# ─────────────────────────────────────────────────────────────────────────────

def score_location(candidate: dict) -> float:
    """
    Score based on geographic fit (Pune/Noida/NCR/Bangalore/etc.) and
    notice period. Candidates outside India score low; willing to relocate
    gets a moderate score.
    Returns a float in [0, 1].
    """
    profile = candidate.get("profile", {})
    signals = candidate.get("redrob_signals", {})

    location = normalize(profile.get("location", ""))
    country = normalize(profile.get("country", ""))
    willing_to_relocate = signals.get("willing_to_relocate", False)
    notice_days = signals.get("notice_period_days", 60)

    # ── Geographic component ──
    in_india = "india" in country or country in {"in", "ind"}
    in_good_city = any(city in location for city in GOOD_LOCATIONS)

    if in_good_city and in_india:
        location_score = 1.0
    elif willing_to_relocate:
        location_score = 0.8
    elif in_india and not in_good_city and not willing_to_relocate:
        location_score = 0.5
    else:
        # Outside India entirely
        location_score = 0.2

    # ── Notice period component ──
    if notice_days <= 30:
        notice_mod = 1.0
    elif notice_days <= 60:
        notice_mod = 0.8
    elif notice_days <= 90:
        notice_mod = 0.6
    else:
        notice_mod = 0.3  # >90 days is a hard disqualifier zone

    final = (location_score * 0.6) + (notice_mod * 0.4)
    return round(final, 4)


# ─────────────────────────────────────────────────────────────────────────────
# COMPONENT 5: EDUCATION SCORE (10%)
# ─────────────────────────────────────────────────────────────────────────────

def score_education(candidate: dict) -> float:
    """
    Score based on institution prestige tier and relevance of field of study.
    Takes the best tier across all education records.
    Returns a float in [0, 1].
    """
    education = candidate.get("education", [])

    if not education:
        return 0.4  # no info, neutral

    tier_map = {"tier_1": 1.0, "tier_2": 0.75, "tier_3": 0.5, "tier_4": 0.3, "unknown": 0.4}

    # Use best (highest) tier score across all degrees
    best_tier_score = max(tier_map.get(e.get("tier", "unknown"), 0.4) for e in education)

    # Field bonus: STEM fields most relevant to AI/ML
    relevant_fields = {
        "computer science", "machine learning", "artificial intelligence",
        "data science", "statistics", "mathematics", "computational",
        "information technology", "software engineering",
    }
    field_bonus = 0.0
    for e in education:
        field = normalize(e.get("field_of_study", ""))
        if any(rf in field for rf in relevant_fields):
            field_bonus = 0.1
            break

    return min(best_tier_score + field_bonus, 1.0)


# ─────────────────────────────────────────────────────────────────────────────
# BEHAVIORAL MULTIPLIER
# ─────────────────────────────────────────────────────────────────────────────

def behavioral_multiplier(candidate: dict) -> float:
    """
    Compute a multiplier [0.4, 1.3] based on platform behavioral signals.
    Penalties for inactivity / ghosting; bonuses for GitHub activity and
    verified identity.
    """
    signals = candidate.get("redrob_signals", {})
    multiplier = 1.0

    # ── Inactivity penalties ──
    inactive_days = days_since(signals.get("last_active_date", ""))
    if inactive_days > 180:
        multiplier *= 0.60  # very stale — not job searching
    elif inactive_days > 90:
        multiplier *= 0.80  # somewhat stale

    # ── Open to work: if not open, less likely to respond ──
    if not signals.get("open_to_work_flag", True):
        multiplier *= 0.75

    # ── Platform engagement quality ──
    if signals.get("recruiter_response_rate", 1.0) < 0.2:
        multiplier *= 0.85  # ignores most recruiter outreach

    if signals.get("interview_completion_rate", 1.0) < 0.5:
        multiplier *= 0.85  # ghosts interviews frequently

    # ── GitHub activity: proxy for hands-on engineering ──
    github = signals.get("github_activity_score", -1)
    if github is not None and github > 70:
        multiplier *= 1.10
    elif github is not None and github > 40:
        multiplier *= 1.05

    # ── Profile completeness ──
    if signals.get("profile_completeness_score", 0) > 85:
        multiplier *= 1.05

    # ── Trust signals ──
    if signals.get("verified_email") and signals.get("verified_phone"):
        multiplier *= 1.03

    # Clamp to prevent extreme values
    return round(max(0.4, min(1.3, multiplier)), 4)


# ─────────────────────────────────────────────────────────────────────────────
# FINAL SCORING
# ─────────────────────────────────────────────────────────────────────────────

def score_candidate(candidate: dict) -> float:
    """
    Compute final score using weighted component scores * behavioral multiplier.
    Returns a float in [0, 1].
    """
    if detect_honeypot(candidate):
        return 0.0

    skills_s = score_skills(candidate)
    career_s = score_career(candidate)
    exp_s = score_experience(candidate)
    loc_s = score_location(candidate)
    edu_s = score_education(candidate)

    # Weighted base score per spec
    base = (
        skills_s * 0.35
        + career_s * 0.25
        + exp_s   * 0.20
        + loc_s   * 0.10
        + edu_s   * 0.10
    )

    multiplier = behavioral_multiplier(candidate)
    final = base * multiplier

    return round(min(final, 1.0), 6)


# ─────────────────────────────────────────────────────────────────────────────
# REASONING GENERATION
# ─────────────────────────────────────────────────────────────────────────────

def generate_reasoning(candidate: dict, score: float) -> str:
    """
    Build a 1-2 sentence reasoning string with SPECIFIC facts from the profile.
    Avoids vague platitudes — surfaces real data points.
    """
    profile = candidate.get("profile", {})
    signals = candidate.get("redrob_signals", {})
    skills = candidate.get("skills", [])
    career = candidate.get("career_history", [])

    yoe = profile.get("years_of_experience", "?")
    title = profile.get("current_title", "Unknown")
    company = profile.get("current_company", "Unknown")
    company_size = profile.get("current_company_size", "?")

    # Top skills (must-have matches first)
    top_skills = []
    for s in skills:
        name = normalize(s.get("name", ""))
        if any(term in name or name in term for term in MUST_HAVE_SKILLS):
            top_skills.append(s.get("name"))
        if len(top_skills) >= 3:
            break
    if not top_skills:
        top_skills = [s.get("name", "") for s in skills[:2]]

    skills_str = "+".join(top_skills) if top_skills else "various skills"

    # Look for production keyword in most recent role description
    prod_signal = ""
    for job in career:
        desc = normalize(job.get("description", ""))
        for kw in PRODUCTION_KEYWORDS[:6]:
            if kw in desc:
                prod_signal = f"production signal: '{kw}'"
                break
        if prod_signal:
            break

    # Activity
    inactive_days = days_since(signals.get("last_active_date", ""))
    if inactive_days == 0:
        activity_str = "active today"
    elif inactive_days == 1:
        activity_str = "active yesterday"
    elif inactive_days < 30:
        activity_str = f"active {inactive_days}d ago"
    elif inactive_days < 90:
        activity_str = f"last active ~{inactive_days // 7}wk ago"
    else:
        activity_str = f"inactive {inactive_days}d"

    open_to = "open to work" if signals.get("open_to_work_flag") else "not open"
    notice = f"{signals.get('notice_period_days', '?')}d notice"
    location = profile.get("location", "unknown")

    # Sentence 1: profile snapshot
    s1 = f"{yoe}yr {title} at {company} ({company_size}); {skills_str}."

    # Sentence 2: activity + production signal
    parts = [activity_str, open_to, notice]
    if prod_signal:
        parts.insert(1, prod_signal)
    s2 = f"Based in {location}; {', '.join(parts)}."

    return f"{s1} {s2}"


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Rank candidates for Senior AI Engineer role")
    parser.add_argument("--candidates", required=True, help="Path to candidates.jsonl (or .jsonl.gz)")
    parser.add_argument("--out", default="submission.csv", help="Output CSV path")
    args = parser.parse_args()

    t0 = time.time()

    print(f"Loading candidates from: {args.candidates}")
    candidates = load_candidates(args.candidates)
    print(f"Loaded {len(candidates):,} candidates")

    # Score all candidates with a progress bar
    print("Scoring candidates...")
    scored = []
    for c in tqdm(candidates, unit="cand", ncols=80):
        s = score_candidate(c)
        if s > 0:
            scored.append((c, s))

    # Sort descending by score, break ties by candidate_id ascending (deterministic)
    scored.sort(key=lambda x: (-x[1], x[0].get("candidate_id", "")))

    top100 = scored[:100]
    actual_ranked = len(top100)

    # Write CSV
    out_path = Path(args.out)
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["candidate_id", "rank", "score", "reasoning"])
        for rank, (cand, score) in enumerate(top100, start=1):
            cid = cand.get("candidate_id", "CAND_0000000")
            reasoning = generate_reasoning(cand, score)
            writer.writerow([cid, rank, f"{score:.6f}", reasoning])

    elapsed = time.time() - t0
    top_cand = top100[0][0].get("candidate_id") if top100 else "N/A"
    top_score = top100[0][1] if top100 else 0.0

    print()
    print("─" * 50)
    print(f"Ranked {actual_ranked} candidates from {len(candidates):,}")
    print(f"Top candidate: {top_cand} (score: {top_score:.4f})")
    print(f"Runtime: {elapsed:.1f} seconds")
    print(f"Output written to: {out_path}")
    print("─" * 50)


if __name__ == "__main__":
    main()
