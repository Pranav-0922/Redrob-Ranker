"""
app.py — Redrob Hackathon: Streamlit Submission Portal + Dashboard
Run: streamlit run app.py
"""

import csv
import gzip
import io
import json
import math
import sys
import time
from datetime import date, datetime
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))
from rank import (
    load_candidates,
    score_candidate,
    generate_reasoning,
    detect_honeypot,
    score_skills,
    score_career,
    score_experience,
    score_location,
    score_education,
    behavioral_multiplier,
    TODAY,
)

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Redrob · AI Candidate Ranker",
    page_icon="🔴",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None,
    }
)

# ─────────────────────────────────────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

/* ── Hide Streamlit chrome including Deploy button ── */
#MainMenu { visibility: hidden; }
header[data-testid="stHeader"] { display: none !important; }
footer { visibility: hidden; }
[data-testid="stToolbar"] { display: none !important; }
.viewerBadge_container__1QSob { display: none !important; }
button[kind="header"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }

/* ── Page background ── */
.main { background: #07070f; }
.block-container { padding: 0 2rem 2rem 2rem !important; max-width: 100% !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0a0a14 0%, #0d0d1a 100%);
    border-right: 1px solid #1a1a28;
}
[data-testid="stSidebar"] * { color: #c8c8dc !important; }

/* ── Top banner ── */
.top-banner {
    background: linear-gradient(135deg, #0d0d20 0%, #111128 50%, #0d0d20 100%);
    border-bottom: 1px solid #1e1e32;
    padding: 22px 32px 20px;
    margin: 0 -2rem 28px -2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: relative;
    overflow: hidden;
}
.top-banner::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #ff3b3b, #6b3bff, #3b8fff, #3bffb0);
}
.banner-title {
    font-size: 1.5rem;
    font-weight: 800;
    color: #eeeef8;
    letter-spacing: -0.035em;
    line-height: 1.1;
}
.banner-sub {
    font-size: 0.78rem;
    color: #5a5a78;
    margin-top: 5px;
    letter-spacing: 0.02em;
}
.live-badge {
    display: flex; align-items: center; gap: 6px;
    background: rgba(52,211,153,0.08);
    border: 1px solid rgba(52,211,153,0.2);
    border-radius: 20px;
    padding: 6px 14px;
    font-size: 0.72rem; font-weight: 700;
    color: #34d399;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}
.live-dot {
    width: 6px; height: 6px; border-radius: 50%;
    background: #34d399;
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
}

/* ── Metric tiles ── */
.metric-tile {
    background: #0f0f1c;
    border: 1px solid #1a1a2c;
    border-radius: 12px;
    padding: 18px 20px;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s, transform 0.15s;
}
.metric-tile:hover { border-color: #2a2a44; transform: translateY(-1px); }
.metric-tile::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 2px;
}
.metric-tile.blue::after   { background: linear-gradient(90deg, #3b3bff, #6b3bff); }
.metric-tile.green::after  { background: linear-gradient(90deg, #34d399, #059669); }
.metric-tile.red::after    { background: linear-gradient(90deg, #ff4040, #dc2626); }
.metric-tile.yellow::after { background: linear-gradient(90deg, #fbbf24, #d97706); }
.metric-tile.purple::after { background: linear-gradient(90deg, #8b5cf6, #6d28d9); }

.metric-label {
    font-size: 0.62rem;
    text-transform: uppercase;
    letter-spacing: 0.13em;
    color: #48486a;
    font-weight: 600;
    margin-bottom: 8px;
}
.metric-value {
    font-size: 2rem;
    font-weight: 800;
    font-family: 'JetBrains Mono', monospace;
    color: #e8e8f8;
    line-height: 1;
    letter-spacing: -0.02em;
}
.metric-value.blue   { color: #6b8fff; }
.metric-value.green  { color: #34d399; }
.metric-value.red    { color: #ff6b6b; }
.metric-value.yellow { color: #fbbf24; }
.metric-value.purple { color: #a78bfa; }
.metric-sub {
    font-size: 0.68rem;
    color: #48486a;
    margin-top: 5px;
    font-family: 'JetBrains Mono', monospace;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* ── Candidate card ── */
.cand-card {
    background: #0f0f1c;
    border: 1px solid #1a1a2c;
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 10px;
    transition: border-color 0.2s, background 0.15s, transform 0.15s;
    position: relative;
}
.cand-card:hover {
    border-color: #3535cc;
    background: #111122;
    transform: translateX(3px);
}
.cand-card-header {
    display: flex; align-items: center;
    justify-content: space-between;
    margin-bottom: 8px;
    flex-wrap: wrap;
    gap: 6px;
}
.rank-num {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    color: #5555dd;
    font-weight: 700;
    background: rgba(85,85,221,0.1);
    border: 1px solid rgba(85,85,221,0.2);
    border-radius: 6px;
    padding: 2px 9px;
    margin-right: 8px;
}
.cand-title {
    font-size: 0.95rem;
    font-weight: 700;
    color: #d8d8f0;
    letter-spacing: -0.01em;
}
.cand-meta { font-size: 0.8rem; color: #5a5a78; }

.score-badge {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.82rem;
    font-weight: 700;
    padding: 4px 12px;
    border-radius: 8px;
}
.score-high { background: rgba(52,211,153,0.1);  color: #34d399; border: 1px solid rgba(52,211,153,0.22); }
.score-mid  { background: rgba(251,191,36,0.1);   color: #fbbf24; border: 1px solid rgba(251,191,36,0.22); }
.score-low  { background: rgba(248,113,113,0.1);  color: #f87171; border: 1px solid rgba(248,113,113,0.22); }

.skill-tag {
    display: inline-block;
    background: rgba(85,85,221,0.07);
    border: 1px solid rgba(85,85,221,0.16);
    border-radius: 5px;
    padding: 2px 8px;
    font-size: 0.68rem;
    color: #7878cc;
    margin: 2px 3px 2px 0;
}
.skill-tag-match {
    background: rgba(52,211,153,0.07);
    border-color: rgba(52,211,153,0.2);
    color: #34d399;
}

.score-bar-wrap {
    background: #1a1a2c;
    border-radius: 3px;
    height: 4px;
    overflow: hidden;
    margin: 8px 0 6px;
}
.score-bar-fill {
    height: 4px;
    border-radius: 3px;
    background: linear-gradient(90deg, #3535cc, #8b5cf6);
}

.comp-row { display: flex; gap: 14px; flex-wrap: wrap; margin-top: 8px; }
.comp-item {
    font-size: 0.65rem;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 600;
}
.reasoning-text {
    font-size: 0.72rem;
    color: #48486a;
    line-height: 1.5;
    margin-top: 5px;
}
.signal-row {
    display: flex; gap: 14px; flex-wrap: wrap;
    margin-top: 6px; align-items: center;
}
.signal { font-size: 0.7rem; color: #5a5a78; display: flex; align-items: center; gap: 4px; }
.sig-dot { width: 5px; height: 5px; border-radius: 50%; display: inline-block; }

/* ── Tabs ── */
[data-baseweb="tab-list"] {
    background: #0f0f1c !important;
    border: 1px solid #1a1a2c !important;
    border-radius: 10px !important;
    padding: 4px !important;
    gap: 2px !important;
}
[data-baseweb="tab"] {
    color: #5a5a78 !important;
    border-radius: 7px !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
}
[aria-selected="true"][data-baseweb="tab"] {
    background: #1a1a2c !important;
    color: #d8d8f0 !important;
}

/* ── Sidebar ── */
.sb-logo { font-size: 1.3rem; font-weight: 800; color: #ff4040; letter-spacing: -0.04em; }
.sb-sub { font-size: 0.68rem; color: #48486a; margin-top: 2px; text-transform: uppercase; letter-spacing: 0.09em; }

/* ── Progress bar ── */
.stProgress > div > div { background: linear-gradient(90deg, #3535cc, #8b5cf6) !important; }

/* ── Inputs ── */
.stTextInput input {
    background: #0f0f1c !important;
    border: 1px solid #1a1a2c !important;
    border-radius: 8px !important;
    color: #d8d8f0 !important;
    font-size: 0.85rem !important;
}
.stTextInput input:focus { border-color: #3535cc !important; box-shadow: 0 0 0 1px #3535cc22 !important; }

/* ── Empty state ── */
.empty-state { text-align: center; padding: 80px 20px; }
.empty-icon { font-size: 3.5rem; margin-bottom: 20px; }
.empty-title { font-size: 1.15rem; font-weight: 700; color: #48486a; margin-bottom: 8px; }
.empty-sub { font-size: 0.82rem; color: #2e2e48; }

.chart-header {
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.11em;
    color: #48486a;
    font-weight: 600;
    margin-bottom: 8px;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────

if "results" not in st.session_state:
    st.session_state.results = None

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown('<div class="sb-logo">🔴 redrob</div>', unsafe_allow_html=True)
    st.markdown('<div class="sb-sub">AI Candidate Intelligence</div>', unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("### Upload Candidates")
    uploaded = st.file_uploader(
        "candidates.jsonl or .jsonl.gz",
        type=["jsonl", "gz"],
        help="Upload the candidate pool to rank",
    )

    st.markdown("### Display Settings")
    top_n = st.slider("Top N to show", min_value=10, max_value=100, value=100, step=10)
    min_score_filter = st.slider("Min score", 0.0, 1.0, 0.0, 0.01)

    st.markdown("---")
    run_btn = st.button("▶  Run Ranker", type="primary", use_container_width=True)

    if st.session_state.results is not None:
        st.markdown("---")
        df_dl = pd.DataFrame(st.session_state.results)
        csv_bytes = df_dl.to_csv(index=False).encode()
        st.download_button(
            "⬇  Download submission.csv",
            data=csv_bytes,
            file_name="submission.csv",
            mime="text/csv",
            use_container_width=True,
        )


# ─────────────────────────────────────────────────────────────────────────────
# TOP BANNER
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="top-banner">
  <div>
    <div class="banner-title">Candidate Ranking Dashboard</div>
    <div class="banner-sub">Senior AI Engineer &nbsp;·&nbsp; Redrob AI &nbsp;·&nbsp; Pune / Noida / Bangalore</div>
  </div>
  <div class="live-badge">
    <div class="live-dot"></div>
    Live Ranker
  </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# MUST-HAVE SKILLS FOR HIGHLIGHTING
# ─────────────────────────────────────────────────────────────────────────────

MUST_HAVE_DISPLAY = {
    "python","llm","rag","embeddings","nlp","faiss","pinecone",
    "qdrant","transformers","langchain","huggingface","sentence-transformers",
    "llms","retrieval","bert","gpt","openai",
}


# ─────────────────────────────────────────────────────────────────────────────
# RUN RANKER
# ─────────────────────────────────────────────────────────────────────────────

def run_ranker(file_bytes: bytes, filename: str):
    t0 = time.time()
    if filename.endswith(".gz"):
        with gzip.open(io.BytesIO(file_bytes), "rt", encoding="utf-8") as f:
            candidates = [json.loads(line) for line in f if line.strip()]
    else:
        text = file_bytes.decode("utf-8")
        candidates = [json.loads(line) for line in text.splitlines() if line.strip()]

    progress_bar = st.progress(0, text="Scoring candidates…")
    all_scored = []
    honeypot_count = 0

    for i, c in enumerate(candidates):
        is_hp = detect_honeypot(c)
        s = 0.0 if is_hp else score_candidate(c)
        all_scored.append((c, s, is_hp))
        if is_hp:
            honeypot_count += 1
        if i % max(1, len(candidates) // 100) == 0:
            progress_bar.progress(i / len(candidates), text=f"Scoring… {i:,}/{len(candidates):,}")

    progress_bar.progress(1.0, text="Done!")
    time.sleep(0.3)
    progress_bar.empty()

    all_scored.sort(key=lambda x: (-x[1], x[0].get("candidate_id", "")))
    top100 = all_scored[:100]

    results = []
    for rank, (cand, score, is_hp) in enumerate(top100, start=1):
        cid = cand.get("candidate_id", "")
        profile = cand.get("profile", {})
        signals = cand.get("redrob_signals", {})
        skills = cand.get("skills", [])

        c_skills = score_skills(cand)
        c_career = score_career(cand)
        c_exp    = score_experience(cand)
        c_loc    = score_location(cand)
        c_edu    = score_education(cand)
        c_behav  = behavioral_multiplier(cand)
        reasoning = generate_reasoning(cand, score)

        top_skill_names = [
            s["name"] for s in sorted(skills, key=lambda x: (
                -{"expert":4,"advanced":3,"intermediate":2,"beginner":1}.get(x.get("proficiency",""),0),
                -x.get("endorsements",0)
            ))
        ][:6]

        results.append({
            "candidate_id": cid,
            "rank": rank,
            "score": round(score, 6),
            "reasoning": reasoning,
            "name": profile.get("anonymized_name", cid),
            "title": profile.get("current_title", ""),
            "company": profile.get("current_company", ""),
            "company_size": profile.get("current_company_size", ""),
            "location": profile.get("location", ""),
            "country": profile.get("country", ""),
            "yoe": profile.get("years_of_experience", 0),
            "open_to_work": signals.get("open_to_work_flag", False),
            "notice_days": signals.get("notice_period_days", 0),
            "github_score": signals.get("github_activity_score", -1),
            "last_active": signals.get("last_active_date", ""),
            "top_skills": top_skill_names,
            "c_skills": round(c_skills, 3),
            "c_career": round(c_career, 3),
            "c_exp":    round(c_exp, 3),
            "c_loc":    round(c_loc, 3),
            "c_edu":    round(c_edu, 3),
            "c_behav":  round(c_behav, 3),
            "is_honeypot": is_hp,
            "total_candidates": len(candidates),
            "honeypot_count": honeypot_count,
        })

    elapsed = time.time() - t0
    return results, all_scored, elapsed


# ─────────────────────────────────────────────────────────────────────────────
# TRIGGER RUN
# ─────────────────────────────────────────────────────────────────────────────

if run_btn:
    if uploaded is None:
        st.error("Please upload a candidates file first.")
    else:
        with st.spinner("Running ranker…"):
            results, all_scored, elapsed = run_ranker(uploaded.read(), uploaded.name)
        st.session_state.results = results
        st.session_state.elapsed = elapsed
        st.session_state.total = results[0]["total_candidates"] if results else 0
        st.session_state.honeypots = results[0]["honeypot_count"] if results else 0
        st.success(f"✅ Ranked {len(results)} candidates from {st.session_state.total:,} in {elapsed:.1f}s")


# ─────────────────────────────────────────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────

if st.session_state.results:
    results = st.session_state.results
    df = pd.DataFrame(results)
    view_df = df[df["score"] >= min_score_filter].head(top_n)

    # ── METRICS ──
    col1, col2, col3, col4, col5 = st.columns(5)

    def metric(col, label, value, sub, color):
        col.markdown(f"""
        <div class="metric-tile {color}">
          <div class="metric-label">{label}</div>
          <div class="metric-value {color}">{value}</div>
          <div class="metric-sub">{sub}</div>
        </div>""", unsafe_allow_html=True)

    metric(col1, "Total Scored",  f"{st.session_state.total:,}",          "candidates",          "blue")
    metric(col2, "Top Score",     f"{df['score'].max():.3f}",              df.iloc[0]['candidate_id'], "green")
    metric(col3, "Honeypots",     str(st.session_state.honeypots),         "detected & zeroed",   "red")
    metric(col4, "Avg Score",     f"{df['score'].mean():.3f}",             "top results",         "yellow")
    metric(col5, "Runtime",       f"{st.session_state.elapsed:.1f}s",      "CPU only",            "purple")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── TABS ──
    tab1, tab2, tab3 = st.tabs(["  🏆  Rankings  ", "  📊  Analytics  ", "  📥  Export  "])

    # ────────────────────────────────────────
    # TAB 1 — RANKINGS
    # ────────────────────────────────────────
    with tab1:
        st.markdown("")

        # Filter row
        fc1, fc2, fc3, fc4 = st.columns([3, 2, 2, 2])
        with fc1:
            search = st.text_input(
                "🔍 Search",
                "",
                placeholder="Search by name, title, company, or skill…",
            )
        with fc2:
            role_options = ["All Roles"] + sorted(df["title"].dropna().unique().tolist())
            role_filter = st.selectbox("Role", role_options)
        with fc3:
            loc_options = ["All Locations"] + sorted(df["location"].dropna().unique().tolist())
            loc_filter = st.selectbox("Location", loc_options)
        with fc4:
            otw_filter = st.selectbox("Availability", ["All", "Open to Work", "Not Open"])

        st.markdown("")

        # Apply filters
        filtered_df = view_df.copy()
        if search:
            filtered_df = filtered_df[filtered_df.apply(
                lambda r: search.lower() in
                f"{r['name']} {r['title']} {r['company']} {' '.join(r['top_skills'])}".lower(),
                axis=1
            )]
        if role_filter != "All Roles":
            filtered_df = filtered_df[filtered_df["title"] == role_filter]
        if loc_filter != "All Locations":
            filtered_df = filtered_df[filtered_df["location"] == loc_filter]
        if otw_filter == "Open to Work":
            filtered_df = filtered_df[filtered_df["open_to_work"] == True]
        elif otw_filter == "Not Open":
            filtered_df = filtered_df[filtered_df["open_to_work"] == False]

        st.caption(f"Showing {len(filtered_df)} candidate{'s' if len(filtered_df) != 1 else ''}")

        for _, row in filtered_df.iterrows():
            score = row["score"]
            badge_cls = "score-high" if score >= 0.6 else ("score-mid" if score >= 0.35 else "score-low")
            bar_w = min(int(score * 100), 100)

            open_dot  = "background:#34d399" if row["open_to_work"] else "background:#48486a"
            open_txt  = "Open to Work" if row["open_to_work"] else "Not Open"
            nd = row["notice_days"]
            notice_dot = "background:#34d399" if nd <= 30 else ("background:#fbbf24" if nd <= 60 else "background:#f87171")
            gh = row["github_score"]
            gh_dot = "background:#34d399" if gh > 70 else ("background:#fbbf24" if gh > 40 else "background:#48486a")
            gh_txt = f"GH {gh:.0f}" if gh >= 0 else "No GitHub"

            skills_html = "".join(
                f'<span class="skill-tag{" skill-tag-match" if any(m in s.lower() for m in MUST_HAVE_DISPLAY) else ""}">{s}</span>'
                for s in row["top_skills"]
            )

            st.markdown(f"""
            <div class="cand-card">
              <div class="cand-card-header">
                <div style="display:flex;align-items:center;flex-wrap:wrap;gap:6px;">
                  <span class="rank-num">#{row['rank']}</span>
                  <span class="cand-title">{row['title']}</span>
                  <span class="cand-meta">· {row['company']} ({row['company_size']}) · {row['yoe']}yr exp</span>
                </div>
                <div style="display:flex;align-items:center;gap:10px;">
                  <span style="font-size:0.75rem;color:#48486a;">{row['location']}</span>
                  <span class="score-badge {badge_cls}">{score:.4f}</span>
                </div>
              </div>
              <div style="margin:6px 0;">{skills_html}</div>
              <div class="score-bar-wrap"><div class="score-bar-fill" style="width:{bar_w}%"></div></div>
              <div class="signal-row">
                <span class="signal"><span class="sig-dot" style="{open_dot}"></span>{open_txt}</span>
                <span class="signal"><span class="sig-dot" style="{notice_dot}"></span>{nd}d notice</span>
                <span class="signal"><span class="sig-dot" style="{gh_dot}"></span>{gh_txt}</span>
              </div>
              <div class="reasoning-text">{row['reasoning']}</div>
              <div class="comp-row">
                <span class="comp-item" style="color:#6b8fff;">Skills {row['c_skills']:.2f}</span>
                <span class="comp-item" style="color:#a78bfa;">Career {row['c_career']:.2f}</span>
                <span class="comp-item" style="color:#06b6d4;">Exp {row['c_exp']:.2f}</span>
                <span class="comp-item" style="color:#34d399;">Loc {row['c_loc']:.2f}</span>
                <span class="comp-item" style="color:#fbbf24;">Edu {row['c_edu']:.2f}</span>
                <span class="comp-item" style="color:#f87171;">×{row['c_behav']:.2f} behav</span>
              </div>
            </div>
            """, unsafe_allow_html=True)

    # ────────────────────────────────────────
    # TAB 2 — ANALYTICS
    # ────────────────────────────────────────
    with tab2:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="chart-header">Score Distribution</div>', unsafe_allow_html=True)
            st.bar_chart(df["score"].value_counts(bins=20).sort_index())
        with c2:
            st.markdown('<div class="chart-header">Years of Experience</div>', unsafe_allow_html=True)
            st.bar_chart(df["yoe"].value_counts().sort_index())

        c3, c4 = st.columns(2)
        with c3:
            st.markdown('<div class="chart-header">Open to Work</div>', unsafe_allow_html=True)
            otw = df["open_to_work"].value_counts()
            otw.index = otw.index.map({True: "Open", False: "Closed"})
            st.bar_chart(otw)
        with c4:
            st.markdown('<div class="chart-header">Notice Period (days)</div>', unsafe_allow_html=True)
            st.bar_chart(df["notice_days"].value_counts().sort_index())

        st.markdown('<div class="chart-header">Component Score Averages</div>', unsafe_allow_html=True)
        comp_df = pd.DataFrame({
            "Component": ["Skills (35%)", "Career (25%)", "Experience (20%)", "Location (10%)", "Education (10%)"],
            "Avg Score": [df["c_skills"].mean(), df["c_career"].mean(),
                          df["c_exp"].mean(), df["c_loc"].mean(), df["c_edu"].mean()]
        })
        st.bar_chart(comp_df.set_index("Component"))

        st.markdown('<div class="chart-header">Top Locations</div>', unsafe_allow_html=True)
        st.bar_chart(df["location"].value_counts().head(10))

    # ────────────────────────────────────────
    # TAB 3 — EXPORT
    # ────────────────────────────────────────
    with tab3:
        st.markdown("### submission.csv")
        export_df = df[["candidate_id", "rank", "score", "reasoning"]].copy()
        st.dataframe(export_df, use_container_width=True, height=400)

        csv_out = export_df.to_csv(index=False).encode()
        st.download_button("⬇  Download submission.csv", data=csv_out,
                           file_name="submission.csv", mime="text/csv")

        st.markdown("---")
        st.markdown("### Full results (with component scores)")
        full_csv = df.to_csv(index=False).encode()
        st.download_button("⬇  Download full_results.csv", data=full_csv,
                           file_name="full_results.csv", mime="text/csv")

        st.markdown("---")
        st.markdown("### Validate format")
        st.code("python validate_submission.py submission.csv", language="bash")

else:
    # Empty state
    st.markdown("""
    <div class="empty-state">
      <div class="empty-icon">🔴</div>
      <div class="empty-title">Upload a candidates file and click Run Ranker</div>
      <div class="empty-sub">
        Accepts <code>.jsonl</code> or <code>.jsonl.gz</code>
        &nbsp;·&nbsp; Up to 100,000 candidates &nbsp;·&nbsp; CPU only
      </div>
    </div>
    """, unsafe_allow_html=True)
