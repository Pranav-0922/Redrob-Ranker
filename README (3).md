# 🎯 Redrob Ranker — AI Candidate Ranking System

> A transparent, rule-based engine that ranks 100,000 candidates for a Senior AI Engineer role in seconds — no black boxes, no API calls, fully explainable.

---

## 📌 Overview

**Redrob Ranker** is a deterministic candidate-ranking system built for the Redrob Hackathon. Given a pool of **100,000 candidate profiles**, it scores and ranks the **top 100 best-fit candidates** for a Senior AI Engineer role, using a weighted, interpretable scoring model instead of an opaque ML classifier.

Every score comes with a **human-readable reasoning string**, so recruiters can see *why* a candidate ranked where they did — not just a number.

The system is intentionally designed to resist the "obvious trap": keyword-stuffed resumes. A candidate listing every AI buzzword under "Skills" but titled *Marketing Manager* will **not** rank highly — the model looks at context, career trajectory, and behavioral signals, not just keyword overlap.

---

## ✨ Key Features

- 🧠 **Explainable scoring** — every ranked candidate includes a plain-English reasoning string
- ⚡ **Fast** — ranks 100,000 candidates in ~10–30 seconds, entirely on CPU
- 🔒 **Fully deterministic** — zero API calls, zero model downloads, same input always produces the same output
- 🕵️ **Honeypot detection** — automatically identifies and zeroes out fake/gamed profiles before ranking
- 📊 **Multi-signal behavioral modifier** — adjusts scores based on real-world engagement signals, not just resume text
- 🖥️ **Dashboard included** — visualize and explore ranked results (`dashboard.html`)
- 🧪 **Sample data generator** — spin up test candidates instantly with `generate_sample.py`

---

## 🧮 How It Works

### 1. Base Score — Five Weighted Components

| Component | Weight | What It Measures |
|---|---|---|
| **Skills** | 35% | Match against must-have NLP/retrieval/LLM skills, weighted by proficiency, endorsements, duration, and assessment scores. Penalizes CV/Speech-only specialists who lack core skills. |
| **Career Quality** | 25% | Rewards product-company experience and evidence of shipping to production (signals like *deployed*, *shipped*, *served*, *pipeline*). Penalizes consulting-only careers and frequent job-hopping. |
| **Experience** | 20% | A bracketed curve that peaks at the **6–8 year** sweet spot for seniority. |
| **Location & Availability** | 10% | Favors candidates based in Pune / Noida / NCR / Bangalore, adjusted by notice period. |
| **Education** | 10% | Institution tier, with a bonus for STEM fields. |

### 2. Behavioral Signal Modifier

The base score is multiplied by a **×0.4 – 1.3 modifier** derived from real-world engagement signals:
- Open-to-work status
- Recency of last activity
- Recruiter / interview response rate
- GitHub activity
- Verified credentials

This ensures a candidate who looks perfect *on paper* but is disengaged or unverifiable doesn't automatically outrank someone with strong, verified real-world signals.

### 3. Honeypot Detection

Before ranking, the system flags and zeroes out fabricated or gamed profiles, including:
- Impossible timelines (overlapping roles, negative durations)
- "Expert" proficiency in skills with zero duration
- Suspiciously perfect, overfit signal combinations designed to trick keyword-based scoring

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Core ranking engine | Python |
| Dashboard / visualization | HTML |
| Dependencies | See `requirements.txt` |

---

## 📁 Project Structure

```
Redrob-Ranker/
├── app.py                 # Application entry point
├── rank.py                # Core ranking engine
├── generate_sample.py     # Generates sample candidate data for testing
├── dashboard.html          # Results dashboard / visualization
├── requirements.txt        # Python dependencies
└── README.md
```

---

## 🚀 Getting Started

### Installation

```bash
git clone https://github.com/Pranav-0922/Redrob-Ranker.git
cd Redrob-Ranker
pip install -r requirements.txt
```

### Run the Ranker

```bash
python rank.py --candidates candidates.jsonl --out submission.csv
```

Gzipped input is also supported:

```bash
python rank.py --candidates candidates.jsonl.gz --out submission.csv
```

### Validate Your Output

```bash
python validate_submission.py submission.csv
```

---

## 📤 Output Format

`submission.csv` contains **exactly 100 rows** with the following columns:

| Column | Description |
|---|---|
| `candidate_id` | Unique identifier for the candidate |
| `rank` | Final rank (1 = best fit) |
| `score` | Computed final score |
| `reasoning` | Human-readable explanation for the ranking |

---

## ⚡ Performance

- Processes **100,000 candidates in ~10–30 seconds**
- Runs entirely on **CPU** — no GPU, no external inference calls
- **Fully deterministic** — reproducible results every run

---

## 🔮 Why Rule-Based Over Black-Box ML?

- **Transparency** — recruiters and candidates can see exactly why a decision was made
- **No training data bias risk** — nothing learned from a skewed historical dataset
- **Speed** — no model inference overhead, scales to 100K+ profiles instantly
- **Auditability** — every weight and rule is inspectable and tunable

---

## 📄 License

This project was built for the Redrob AI Hackathon. Feel free to reach out for usage or collaboration inquiries.

---

<p align="center">Built with 🧠 for the Redrob AI Hackathon</p>
