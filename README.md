# Redrob Hackathon — AI Candidate Ranking System

## Approach

A transparent, rule-based scoring system that ranks 100,000 candidates for a Senior AI Engineer role across five weighted components: **Skills** (35%) — matching must-have NLP/retrieval/LLM skills with proficiency, endorsement, duration, and assessment-score bonuses while penalizing CV/Speech-only profiles; **Career Quality** (25%) — rewarding product-company backgrounds and production deployment signals (deployed/shipped/served/pipeline) while penalising consulting-only careers and job-hopping; **Experience** (20%) — a bracketed curve centred on the 6–8 year sweet spot; **Location & Availability** (10%) — Pune/Noida/NCR/Bangalore targeting with notice-period modifiers; **Education** (10%) — institution tier with a STEM field bonus. The base score is then multiplied by a behavioral signal modifier (×0.4–1.3) derived from open-to-work status, last-activity recency, recruiter/interview response rates, GitHub activity, and verified credentials. Honeypot profiles (impossible timelines, expert-but-zero-duration skills, perfectly-over-fitted signals) are zeroed out before ranking. The system runs on CPU in ~10–30 seconds for 100K candidates.

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
python rank.py --candidates candidates.jsonl --out submission.csv
```

For gzipped input:
```bash
python rank.py --candidates candidates.jsonl.gz --out submission.csv
```

## Validate

```bash
python validate_submission.py submission.csv
```

## Output

`submission.csv` — exactly 100 rows, columns: `candidate_id, rank, score, reasoning`
