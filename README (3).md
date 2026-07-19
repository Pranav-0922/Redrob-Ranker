# 🎯 Redrob Ranker

### An Explainable, Rule-Based AI Candidate Ranking System

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)
![HTML](https://img.shields.io/badge/HTML-Dashboard-E34F26?style=for-the-badge&logo=html5)
![CPU Only](https://img.shields.io/badge/Compute-CPU%20Only-success?style=for-the-badge)
![Deterministic](https://img.shields.io/badge/Output-Deterministic-informational?style=for-the-badge)
![No API Calls](https://img.shields.io/badge/API%20Calls-Zero-critical?style=for-the-badge)
![Explainable AI](https://img.shields.io/badge/Explainable-Rule--Based%20Scoring-purple?style=for-the-badge)
![Hackathon](https://img.shields.io/badge/Built%20For-Redrob%20AI%20Hackathon-orange?style=for-the-badge)

---

## Executive Summary

Hiring at scale is a ranking problem hiding inside a trust problem. When a black-box model decides who gets shortlisted, recruiters can't explain *why* — and candidates can't understand what they were measured against.

**Redrob Ranker** solves this by replacing opaque ML scoring with a **fully transparent, rule-based ranking engine**. Given **100,000 candidate profiles**, it identifies and ranks the **top 100 best-fit candidates** for a Senior AI Engineer role — and attaches a plain-English explanation to every single decision.

It is deliberately built to resist the most common resume-screening exploit: keyword stuffing. A profile listing every AI buzzword under "Skills" but titled *Marketing Manager* will not rank highly here — the engine reasons about context, career trajectory, and verified behavior, not just text overlap.

> **Can a fully explainable, deterministic system out-rank a black box — and do it fast enough for 100K candidates?**

---

## Repository Highlights

* ⚡ Ranks 100,000 candidates in ~10–30 seconds — entirely on CPU
* 🧠 Every ranked candidate ships with a human-readable reasoning string
* 🔒 Zero API calls, zero model downloads — fully deterministic and reproducible
* 🕵️ Built-in honeypot detection to catch fabricated / gamed profiles
* 📊 Multi-signal behavioral modifier layered on top of the base score
* 🖥️ Included dashboard for visual exploration of results
* 🧪 Sample data generator for instant local testing

---

## Business Objective

The goal of this project is to demonstrate that candidate ranking at scale doesn't require sacrificing transparency for speed. It's built to support:

* Transparent, auditable hiring pipelines
* Recruiter trust through explainable scoring
* Fast shortlisting across massive candidate pools
* Resistance to resume keyword-gaming
* A reusable scoring framework adaptable to other roles

---

## The Challenge

Given 100,000 candidate profiles — each with structured attributes, career history, skills, education, and behavioral signals — rank the top 100 candidates for a **Senior AI Engineer (Founding Team)** role.

The brief explicitly warns against the obvious trap:

> *"The right answer is NOT to find candidates whose skills section contains the most AI keywords. A candidate who has all the AI keywords listed as skills but whose title is 'Marketing Manager' is not a fit."*

Redrob Ranker is built ground-up to solve for that trap.

---

## How It Works

### 1️⃣ Base Score — Five Weighted Components

| Component | Weight | What It Measures |
|---|---|---|
| **Skills** | 35% | Match against must-have NLP/retrieval/LLM skills, weighted by proficiency, endorsements, duration, and assessment scores. Penalizes CV/Speech-only specialists lacking core skills. |
| **Career Quality** | 25% | Rewards product-company experience and evidence of shipping to production (signals like *deployed*, *shipped*, *served*, *pipeline*). Penalizes consulting-only careers and job-hopping. |
| **Experience** | 20% | A bracketed curve peaking at the **6–8 year** seniority sweet spot. |
| **Location & Availability** | 10% | Favors Pune / Noida / NCR / Bangalore, adjusted by notice period. |
| **Education** | 10% | Institution tier, with a bonus for STEM fields. |

### 2️⃣ Behavioral Signal Modifier

The base score is multiplied by a **×0.4 – 1.3 modifier**, derived from:

* Open-to-work status
* Recency of last activity
* Recruiter / interview response rate
* GitHub activity
* Verified credentials

This prevents a candidate who looks flawless *on paper* but is disengaged or unverifiable from automatically outranking a strong, verified, actively-engaged candidate.

### 3️⃣ Honeypot Detection

Before ranking, profiles are screened for manipulation and zeroed out if they show:

* Impossible timelines (overlapping roles, negative durations)
* "Expert" proficiency claimed with zero duration
* Suspiciously perfect, overfit signal combinations designed to game keyword scoring

---

## Key Analytical Questions the System Answers

**Candidate Fit**
* Which candidates genuinely match the role vs. those who only match on keywords?
* How does career trajectory affect ranking beyond raw skill match?

**Signal Reliability**
* How much should behavioral/engagement data influence a resume-based score?
* Which profiles are fabricated or gamed, and how are they filtered out?

**Scalability**
* Can a fully rule-based system rank 100K+ candidates fast enough to be practical?
* Is the output reproducible and auditable at that scale?

---

## Output Format

`submission.csv` — exactly **100 rows**:

| Column | Description |
|---|---|
| `candidate_id` | Unique identifier for the candidate |
| `rank` | Final rank (1 = best fit) |
| `score` | Computed final score |
| `reasoning` | Human-readable explanation for the ranking |

---

## Technology Stack

| Category | Tools |
|---|---|
| Core Language | Python |
| Ranking Engine | Custom rule-based scoring (`rank.py`) |
| Application Layer | `app.py` |
| Visualization / Dashboard | HTML (`dashboard.html`) |
| Test Data Generation | `generate_sample.py` |
| Dependency Management | `requirements.txt` |
| Domain | AI Recruitment, Explainable Ranking Systems |

---

## Project Architecture

```text
Redrob-Ranker/
│
├── README.md
├── requirements.txt
├── .gitignore
│
├── app.py                 # Application entry point
├── rank.py                # Core rule-based ranking engine
├── generate_sample.py     # Generates sample candidate data for testing
├── dashboard.html          # Results dashboard / visualization
│
├── data/
│   └── candidates.jsonl   # Input candidate dataset (not tracked in repo)
│
└── output/
    └── submission.csv     # Generated ranking output
```

---

## Getting Started

### Clone the Repository

```bash
git clone https://github.com/Pranav-0922/Redrob-Ranker.git
cd Redrob-Ranker
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Generate Sample Data (optional)

```bash
python generate_sample.py
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

## Major Design Principles

### 1. Transparency Over Black Boxes
Every score can be traced back to the exact rule that produced it — no hidden weights, no unexplainable outputs.

### 2. Resistance to Gaming
The honeypot layer actively hunts for manipulated profiles instead of assuming clean data.

### 3. Speed at Scale
100,000 profiles processed in under 30 seconds, with zero external dependencies or network calls.

### 4. Reproducibility
Fully deterministic — the same input always produces the same ranked output, every time.

---

## Future Enhancements

* Configurable scoring weights via a YAML/JSON config file
* Interactive Streamlit/React dashboard replacing static HTML
* Support for multiple job roles / JD templates
* Score sensitivity analysis (how much each component drives the final rank)
* Batch comparison mode across multiple candidate pools
* Exportable candidate scorecards (PDF/CSV per candidate)

---

## Results & Impact

Redrob Ranker demonstrates that explainability and scale are not mutually exclusive in candidate ranking. By combining a transparent, weighted scoring model with behavioral signal analysis and built-in fraud detection, it delivers hiring recommendations that are fast, reproducible, and — most importantly — **defensible**.

---

<p align="center">Built with 🧠 for the Redrob AI Hackathon</p>
