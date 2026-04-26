# 🧠 AI-Powered Skill Assessment & Personalised Learning Plan Agent

**Built for Catalyst Hackathon — Deccan AI**  
**Author:** Yash Rana  
**Live Demo:** [https://ai-powered-skill-assessment-kprrpapppb89bah5eggnfey.streamlit.app](https://ai-powered-skill-assessment-kprrpapppb89bah5eggnfey.streamlit.app)

---

## What It Does

A resume tells you what someone *claims* to know — not how well they actually know it.

This agent takes a **Job Description** and a **candidate's resume**, identifies the skills that matter most (present in both JD and resume), conversationally assesses real proficiency through adaptive questioning, and generates a **personalised learning plan** focused on gaps and adjacent skills the candidate can realistically acquire.

---

## How It Works — 3 Stages

### Stage 1 — Analyse
Paste a JD + upload or paste a resume. The agent extracts:
- Top 4 most critical overlapping skills (claimed by candidate + required by JD)
- Skills in JD but missing from resume (flagged as gaps)
- Seniority level (junior / mid / senior / lead)
- Relevant projects from the resume

### Stage 2 — Assess
Conversational assessment per skill:
- Questions are **calibrated to the seniority level** required by the JD
- Difficulty **adapts based on the candidate's answers** (escalates if strong, simplifies if struggling)
- Questions are tied to the candidate's **actual projects** where relevant
- Feedback is human and mentor-like — no harsh scoring mid-conversation

### Stage 3 — Plan
Once all skills are assessed:
- Overall match score (%)
- Per-skill scores with honest verdict
- Skills to add to resume (gaps from JD)
- Prioritised learning plan with curated resources and time estimates
- Week-by-week action plan
- Realistic readiness verdict

---

## What Makes It Different

| Feature | Generic Tools | This Agent |
|---|---|---|
| Assesses only relevant skills | ❌ Tests everything | ✅ JD + resume overlap only |
| Seniority-calibrated questions | ❌ One-size-fits-all | ✅ Junior → Lead, different depth |
| Adaptive difficulty | ❌ Fixed question bank | ✅ Escalates/simplifies per answer |
| Tied to candidate's projects | ❌ Generic questions | ✅ References actual resume projects |
| Gap vs improvement split | ❌ Combined | ✅ Assessed skills vs missing skills separated |
| Curated resources | ❌ Hallucinated links | ✅ Hardcoded verified sources |

---

## Architecture
<img width="699" height="556" alt="image" src="https://github.com/user-attachments/assets/bdaca73f-c0b1-4dcc-af62-9d7ff36c37a4" />

**Seniority Thresholds (escalation logic):**
| Level | Escalate at | Drop at |
|-------|-------------|---------|
| Junior | 7/10 | <4 |
| Mid | 8/10 | <5 |
| Senior | 8/10 | <6 |
| Lead | 9/10 | <7 |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend + Backend | Streamlit (Python) |
| LLM | Groq API — `llama-3.3-70b-versatile` |
| PDF Parsing | pypdf |
| Learning Resources | Curated hardcoded dictionary (zero hallucination) |
| Hosting | Streamlit Community Cloud |

---

## Local Setup

**1. Clone the repo**
```bash
git clone https://github.com/YR36/AI-Powered-Skill-Assessment.git
cd AI-Powered-Skill-Assessment
```

**2. Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Add your API key**

Create a `.env` file:
GROQ_API_KEY=your_groq_api_key_here

Get a free key at [console.groq.com](https://console.groq.com)

**5. Run**
```bash
streamlit run app.py
```
Opens at `http://localhost:8501`

---

## Sample Input

**Job Description:**
> Senior Backend Engineer — 5+ years Python, FastAPI, PostgreSQL, Docker, AWS. Responsible for designing scalable microservices and leading a team of 3.

**Resume:**
> Yash Rana — 3 years experience. Skills: Python, FastAPI, PostgreSQL, React. Projects: Built a real-time fraud detection API handling 10k req/s. Deployed ML models using Flask and Docker.

**Output:**
- Skills assessed: Python, FastAPI, PostgreSQL, Docker
- Gap flagged: AWS
- Match score: 68%
- Readiness verdict: 68% ready now. Realistically 85% in 6-8 weeks with focus on AWS and system design.

---

## Project Structure
AI-Powered-Skill-Assessment/
├── app.py              # Streamlit UI + 3-stage flow logic
├── utils.py            # Groq API calls, PDF parsing, JSON handling
├── prompts.py          # All LLM prompt templates
├── resources.py        # Curated resources — 35 skills, verified URLs
├── requirements.txt    # Python dependencies
├── .streamlit/
│   └── config.toml     # Dark theme config
└── README.md
---

## Scoring Logic

Each skill is assessed over N questions (2–4, user-selected):
- Each answer scored 0–10 internally by the LLM
- Score considers: technical accuracy, depth, relevance to seniority
- Per-skill score = average across all questions
- Overall match score = weighted average of skill scores vs JD requirements
- Gaps (missing skills) reduce the overall match score

Feedback shown to the candidate is mentor-style — no raw numbers during assessment, only on the final dashboard.

---
