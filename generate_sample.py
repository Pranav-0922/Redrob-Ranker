"""
generate_sample.py — Generate rich sample candidate data for Redrob Ranker
Creates 200 candidates with realistic names, roles, skills, companies, locations
"""

import json
import random
from datetime import date, timedelta

# ── Real Indian names ──
FIRST_NAMES = [
    "Arjun", "Priya", "Rahul", "Ananya", "Vikram", "Neha", "Rohan", "Pooja",
    "Amit", "Divya", "Karan", "Shreya", "Aditya", "Meera", "Nikhil", "Riya",
    "Siddharth", "Kavya", "Varun", "Nisha", "Pranav", "Tanvi", "Harsh", "Simran",
    "Kunal", "Isha", "Akash", "Aditi", "Manish", "Swati", "Deepak", "Anjali",
    "Gaurav", "Pallavi", "Vivek", "Sneha", "Rajesh", "Preeti", "Suresh", "Komal",
    "Mohit", "Kritika", "Tarun", "Bhavna", "Yash", "Muskan", "Shiv", "Ritika",
    "Abhishek", "Sakshi", "Ravi", "Nidhi", "Saurabh", "Megha", "Ashish", "Prerna",
    "Vishal", "Sonali", "Ajay", "Rekha", "Pankaj", "Urvashi", "Dinesh", "Monika",
]

LAST_NAMES = [
    "Sharma", "Patel", "Singh", "Kumar", "Verma", "Gupta", "Mehta", "Shah",
    "Joshi", "Nair", "Reddy", "Rao", "Iyer", "Pillai", "Bose", "Chatterjee",
    "Mishra", "Tiwari", "Pandey", "Dubey", "Sinha", "Saxena", "Agarwal", "Bansal",
    "Kapoor", "Malhotra", "Khanna", "Chopra", "Sethi", "Bhatia", "Arora", "Kohli",
    "Yadav", "Chauhan", "Rajput", "Thakur", "Desai", "Jain", "Trivedi", "Bhatt",
]

# ── Job titles ──
TITLES = [
    "Senior AI Engineer",
    "ML Engineer",
    "NLP Engineer",
    "AI Research Engineer",
    "Data Scientist",
    "Senior Data Scientist",
    "LLM Engineer",
    "Applied AI Engineer",
    "Deep Learning Engineer",
    "AI Platform Engineer",
    "Conversational AI Engineer",
    "Search & Ranking Engineer",
    "MLOps Engineer",
    "AI Infrastructure Engineer",
    "NLP Research Scientist",
]

# ── Companies ──
PRODUCT_COMPANIES = [
    "Google", "Microsoft", "Amazon", "Meta", "Apple",
    "Flipkart", "Zomato", "Swiggy", "Razorpay", "Paytm",
    "Meesho", "CRED", "PhonePe", "Ola", "Byju's",
    "Zepto", "Groww", "Zerodha", "Nykaa", "Urban Company",
    "ShareChat", "Dailyhunt", "Glance", "InMobi", "Freshworks",
    "Zoho", "Juspay", "Setu", "Unacademy", "Vedantu",
]

CONSULTING_COMPANIES = [
    "TCS", "Infosys", "Wipro", "Accenture", "Cognizant",
    "Capgemini", "HCL Technologies", "Tech Mahindra",
]

COMPANY_SIZES = ["startup", "mid", "large", "enterprise"]

# ── Locations ──
LOCATIONS = [
    "Pune, India", "Noida, India", "Bangalore, India",
    "Gurugram, India", "Mumbai, India", "Hyderabad, India",
    "Delhi NCR, India", "Chennai, India", "Kolkata, India",
    "Ahmedabad, India", "Jaipur, India",
]

# ── Skills pool with metadata ──
MUST_HAVE_SKILLS = [
    {"name": "Python",                "proficiency": "expert",       "duration_months": 60, "endorsements": 45},
    {"name": "LLM",                   "proficiency": "expert",       "duration_months": 24, "endorsements": 32},
    {"name": "RAG",                   "proficiency": "advanced",     "duration_months": 18, "endorsements": 28},
    {"name": "Embeddings",            "proficiency": "expert",       "duration_months": 36, "endorsements": 30},
    {"name": "NLP",                   "proficiency": "expert",       "duration_months": 48, "endorsements": 38},
    {"name": "FAISS",                 "proficiency": "advanced",     "duration_months": 20, "endorsements": 22},
    {"name": "Pinecone",              "proficiency": "intermediate", "duration_months": 12, "endorsements": 14},
    {"name": "Transformers",          "proficiency": "expert",       "duration_months": 30, "endorsements": 35},
    {"name": "Fine-tuning",           "proficiency": "advanced",     "duration_months": 18, "endorsements": 25},
    {"name": "LangChain",             "proficiency": "advanced",     "duration_months": 14, "endorsements": 20},
    {"name": "Sentence Transformers", "proficiency": "advanced",     "duration_months": 16, "endorsements": 18},
    {"name": "OpenAI API",            "proficiency": "expert",       "duration_months": 20, "endorsements": 26},
    {"name": "HuggingFace",           "proficiency": "expert",       "duration_months": 28, "endorsements": 34},
    {"name": "Vector Search",         "proficiency": "advanced",     "duration_months": 15, "endorsements": 19},
    {"name": "Semantic Search",       "proficiency": "advanced",     "duration_months": 18, "endorsements": 21},
    {"name": "Information Retrieval", "proficiency": "advanced",     "duration_months": 24, "endorsements": 16},
    {"name": "GPT-4",                 "proficiency": "advanced",     "duration_months": 12, "endorsements": 23},
    {"name": "BERT",                  "proficiency": "expert",       "duration_months": 30, "endorsements": 29},
    {"name": "Qdrant",                "proficiency": "intermediate", "duration_months": 10, "endorsements": 12},
    {"name": "Weaviate",              "proficiency": "intermediate", "duration_months": 8,  "endorsements": 10},
    {"name": "LlamaIndex",            "proficiency": "advanced",     "duration_months": 10, "endorsements": 15},
    {"name": "Ranking / NDCG",        "proficiency": "advanced",     "duration_months": 20, "endorsements": 17},
]

GOOD_TO_HAVE_SKILLS = [
    {"name": "PyTorch",       "proficiency": "advanced",     "duration_months": 36, "endorsements": 30},
    {"name": "FastAPI",       "proficiency": "advanced",     "duration_months": 24, "endorsements": 18},
    {"name": "Docker",        "proficiency": "intermediate", "duration_months": 30, "endorsements": 22},
    {"name": "Kubernetes",    "proficiency": "intermediate", "duration_months": 18, "endorsements": 15},
    {"name": "MLflow",        "proficiency": "intermediate", "duration_months": 14, "endorsements": 12},
    {"name": "Redis",         "proficiency": "intermediate", "duration_months": 20, "endorsements": 14},
    {"name": "Elasticsearch", "proficiency": "advanced",     "duration_months": 24, "endorsements": 20},
    {"name": "Spark",         "proficiency": "intermediate", "duration_months": 18, "endorsements": 16},
    {"name": "Kafka",         "proficiency": "intermediate", "duration_months": 12, "endorsements": 10},
    {"name": "LoRA",          "proficiency": "advanced",     "duration_months": 10, "endorsements": 18},
    {"name": "TensorFlow",    "proficiency": "advanced",     "duration_months": 30, "endorsements": 24},
    {"name": "XGBoost",       "proficiency": "intermediate", "duration_months": 20, "endorsements": 14},
    {"name": "DBT",           "proficiency": "beginner",     "duration_months": 8,  "endorsements": 6},
    {"name": "AWS SageMaker", "proficiency": "intermediate", "duration_months": 16, "endorsements": 13},
    {"name": "GCP Vertex AI", "proficiency": "intermediate", "duration_months": 12, "endorsements": 11},
]

# ── Education ──
INSTITUTIONS = [
    {"institution": "IIT Bombay",     "degree": "B.Tech", "field_of_study": "Computer Science", "end_year": 2018, "tier": "tier_1"},
    {"institution": "IIT Delhi",      "degree": "M.Tech", "field_of_study": "Artificial Intelligence", "end_year": 2019, "tier": "tier_1"},
    {"institution": "IIT Madras",     "degree": "B.Tech", "field_of_study": "Computer Science", "end_year": 2017, "tier": "tier_1"},
    {"institution": "IISc Bangalore", "degree": "M.Tech", "field_of_study": "Machine Learning", "end_year": 2020, "tier": "tier_1"},
    {"institution": "BITS Pilani",    "degree": "B.E.",   "field_of_study": "Computer Science", "end_year": 2018, "tier": "tier_2"},
    {"institution": "NIT Trichy",     "degree": "B.Tech", "field_of_study": "Information Technology", "end_year": 2019, "tier": "tier_2"},
    {"institution": "VIT Vellore",    "degree": "B.Tech", "field_of_study": "Computer Science", "end_year": 2020, "tier": "tier_3"},
    {"institution": "Pune University","degree": "B.E.",   "field_of_study": "Computer Engineering", "end_year": 2019, "tier": "tier_3"},
    {"institution": "DTU Delhi",      "degree": "B.Tech", "field_of_study": "Software Engineering", "end_year": 2018, "tier": "tier_2"},
    {"institution": "IIIT Hyderabad", "degree": "B.Tech", "field_of_study": "Computer Science", "end_year": 2019, "tier": "tier_1"},
]

# ── Job descriptions with production signals ──
JOB_DESCRIPTIONS = [
    "Built and deployed production RAG pipeline serving 2M+ daily users with P99 latency < 200ms.",
    "Shipped fine-tuned LLM for document understanding; improved accuracy by 18% over baseline.",
    "Designed and launched semantic search system using FAISS and sentence-transformers at scale.",
    "Led development of NLP pipeline for entity extraction; deployed via FastAPI on Kubernetes.",
    "Built real-time recommendation system using embeddings; served 500K users in production.",
    "Developed and maintained vector search microservice with Pinecone; monitored with Grafana.",
    "Shipped conversational AI system using LangChain + GPT-4; integrated with live CRM.",
    "Built A/B testing framework for ranking models; improved NDCG@10 by 12% over 3 months.",
    "Designed ML pipeline for text classification; deployed on AWS SageMaker with auto-scaling.",
    "Built and deployed LLM fine-tuning pipeline using LoRA; reduced inference cost by 40%.",
    "Developed information retrieval system with BM25 + dense retrieval hybrid for enterprise search.",
    "Shipped production-grade NER model with 94% F1; integrated into data pipeline serving clients.",
    "Led migration of legacy ML models to scalable microservices; improved throughput 3x.",
    "Built embedding-based deduplication system processing 10M records daily in production.",
    "Designed and shipped multimodal AI pipeline; presented at internal tech conference.",
]

random.seed(42)
records = []
used_names = set()

for i in range(200):
    # Generate unique name
    while True:
        fname = random.choice(FIRST_NAMES)
        lname = random.choice(LAST_NAMES)
        full_name = f"{fname} {lname}"
        if full_name not in used_names:
            used_names.add(full_name)
            break

    cid = f"CAND_{i:07d}"

    # Decide candidate quality tier
    tier = random.choices(["high", "mid", "low"], weights=[0.3, 0.5, 0.2])[0]

    if tier == "high":
        must_count   = random.randint(5, 8)
        good_count   = random.randint(3, 5)
        yoe          = random.randint(5, 10)
        company      = random.choice(PRODUCT_COMPANIES[:15])
        company_size = random.choice(["mid", "large", "enterprise"])
        notice_days  = random.choice([0, 15, 30])
        open_to_work = random.choices([True, False], weights=[0.75, 0.25])[0]
        github_score = random.randint(60, 95)
        active_days_ago = random.randint(0, 30)
        resp_rate    = round(random.uniform(0.7, 1.0), 2)
        interview_rate = round(random.uniform(0.75, 1.0), 2)
        completeness = random.randint(85, 100)
        edu          = random.choice(INSTITUTIONS[:5])
    elif tier == "mid":
        must_count   = random.randint(3, 6)
        good_count   = random.randint(2, 4)
        yoe          = random.randint(3, 8)
        company      = random.choice(PRODUCT_COMPANIES)
        company_size = random.choice(COMPANY_SIZES)
        notice_days  = random.choice([30, 60, 90])
        open_to_work = random.choices([True, False], weights=[0.5, 0.5])[0]
        github_score = random.randint(30, 70)
        active_days_ago = random.randint(0, 90)
        resp_rate    = round(random.uniform(0.4, 0.8), 2)
        interview_rate = round(random.uniform(0.5, 0.85), 2)
        completeness = random.randint(65, 90)
        edu          = random.choice(INSTITUTIONS)
    else:  # low
        must_count   = random.randint(1, 3)
        good_count   = random.randint(1, 3)
        yoe          = random.randint(1, 4)
        company      = random.choice(CONSULTING_COMPANIES + PRODUCT_COMPANIES[15:])
        company_size = random.choice(["startup", "mid"])
        notice_days  = random.choice([60, 90, 120])
        open_to_work = random.choices([True, False], weights=[0.3, 0.7])[0]
        github_score = random.randint(0, 40)
        active_days_ago = random.randint(60, 300)
        resp_rate    = round(random.uniform(0.1, 0.5), 2)
        interview_rate = round(random.uniform(0.2, 0.6), 2)
        completeness = random.randint(40, 70)
        edu          = random.choice(INSTITUTIONS[5:])

    # Build skills list
    must_sample = random.sample(MUST_HAVE_SKILLS, min(must_count, len(MUST_HAVE_SKILLS)))
    good_sample = random.sample(GOOD_TO_HAVE_SKILLS, min(good_count, len(GOOD_TO_HAVE_SKILLS)))

    # Add some variance to endorsements/duration
    def vary(skill):
        s = dict(skill)
        s["endorsements"] = max(0, s["endorsements"] + random.randint(-8, 8))
        s["duration_months"] = max(1, s["duration_months"] + random.randint(-6, 6))
        return s

    skills = [vary(s) for s in must_sample + good_sample]

    last_active = (date.today() - timedelta(days=active_days_ago)).strftime("%Y-%m-%d")

    # Build career history
    num_jobs = random.randint(1, 3)
    career = []
    for j in range(num_jobs):
        co = random.choice(PRODUCT_COMPANIES if tier != "low" else CONSULTING_COMPANIES)
        career.append({
            "company": co,
            "title": random.choice(TITLES),
            "duration_months": random.randint(12, 48),
            "is_current": (j == 0),
            "description": random.choice(JOB_DESCRIPTIONS),
        })

    # Assessment scores
    assessment = {}
    for s in must_sample[:3]:
        assessment[s["name"]] = random.randint(60, 99)

    records.append({
        "candidate_id": cid,
        "profile": {
            "name": full_name,
            "anonymized_name": full_name,
            "current_title": random.choice(TITLES),
            "current_company": company,
            "current_company_size": company_size,
            "location": random.choice(LOCATIONS),
            "country": "India",
            "years_of_experience": yoe,
            "summary": f"{yoe} years of experience in AI/ML with focus on NLP and LLMs.",
        },
        "skills": skills,
        "education": [edu],
        "career_history": career,
        "redrob_signals": {
            "open_to_work_flag": open_to_work,
            "last_active_date": last_active,
            "notice_period_days": notice_days,
            "github_activity_score": github_score,
            "recruiter_response_rate": resp_rate,
            "interview_completion_rate": interview_rate,
            "profile_completeness_score": completeness,
            "verified_email": random.choice([True, True, True, False]),
            "verified_phone": random.choice([True, True, False]),
            "skill_assessment_scores": assessment,
            "offer_acceptance_rate": round(random.uniform(0.5, 0.95), 2),
            "willing_to_relocate": random.choice([True, False]),
        },
    })

with open("candidates.jsonl", "w", encoding="utf-8") as f:
    for r in records:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

print(f"Done! candidates.jsonl created with {len(records)} candidates.")
print(f"  High quality: {sum(1 for r in records if r['redrob_signals']['github_activity_score'] > 60)}")
print(f"  Open to work: {sum(1 for r in records if r['redrob_signals']['open_to_work_flag'])}")
print(f"  Unique names: {len(used_names)}")
