# 🧠 AI Skill Assessment & Personalised Learning Plan Agent

**Built for Catalyst Hackathon — Deccan AI**

**Author:** Yash Rana

**Live Demo:** [Try it here →](https://ai-powered-skill-assessment-kprrpapppb89bah5eggnfey.streamlit.app)

---

## The Problem

When someone applies for a job, their resume says *what* they know.
But nobody actually checks *how well* they know it — until the interview.

By then it's too late. The candidate is underprepared. The interviewer is disappointed. Time is wasted on both sides.

---

## What This Does

This agent acts like a sharp technical interviewer that also cares about your growth.

You give it two things:
- A **Job Description** — what the role needs
- Your **Resume** — what you claim to know

It gives you back three things:
1. **An honest conversation** — it asks you real questions about the skills that actually matter (the ones on both the JD and your resume), starting easy and getting harder based on how you answer
2. **A clear picture** — where you're strong, where you're weak, and what's missing entirely
3. **A real plan** — not "just Google it", but a week-by-week learning plan with verified resources, time estimates, and a honest readiness verdict

---

## Why It's Different

Most tools either scan your resume for keywords or ask you generic quiz questions. This agent does neither.

| What others do | What this does |
|---|---|
| Tests every skill mentioned anywhere | Only tests skills you claimed AND the job needs |
| Same questions for junior and senior | Calibrates difficulty to the seniority level in the JD |
| Generic questions from a question bank | Questions tied to your actual projects from your resume |
| Shows you a score and moves on | Gives you mentor-style feedback explaining what you got right and what was missing |
| Suggests random courses | Maps gaps to verified, curated resources — no broken links |

---

## How It Works (Plain English)

**Step 1 — Read everything**
You paste the Job Description and upload your resume. The agent reads both and figures out: what does this job actually need? What has this person actually built? Where do those two things overlap?

**Step 2 — Have a real conversation**
For each skill that overlaps, the agent asks you questions. Not trivia. Real questions like a senior engineer would ask in an interview. If you answer well, it gets harder. If you struggle, it tries a different angle. The seniority level in the JD determines how tough it gets — a junior role stays at fundamentals, a senior role pushes into system design.

You never see a score during the conversation. You just get honest feedback from what feels like a knowledgeable mentor.

**Step 3 — Get your plan**
Once the conversation is done, you get a dashboard showing:
- How you scored on each skill (with colour coding — green, yellow, red)
- What skills the job needs that aren't on your resume at all
- A prioritised list of what to work on first, and why
- A week-by-week action plan with measurable goals
- Curated resources (real links that work, not AI-hallucinated URLs)
- A readiness verdict: "You're 68% ready now. Realistically 85% in 6–8 weeks."

---

## Architecture

<img width="699" height="556" alt="image" src="https://github.com/user-attachments/assets/13194d9a-5900-49f2-b069-a2182a872e65" />


**How the scoring works:**
Every answer is scored 0–10 by the LLM based on technical accuracy, depth, and whether it matches the seniority level expected. The score is never shown mid-conversation — only on the final dashboard. The next question adapts based on the previous score.

Seniority thresholds (when difficulty escalates or drops):

| Level | Escalate if score ≥ | Simplify if score < |
|-------|---|---|
| Junior | 7 | 4 |
| Mid | 8 | 5 |
| Senior | 8 | 6 |
| Lead | 9 | 7 |

---

## Tech Stack

| What | Why |
|---|---|
| **Streamlit** | Fast to build, clean UI, deploys in one push |
| **Groq API** (llama-3.3-70b-versatile) | Fast open-source LLM, production tier, great at conversation + JSON |
| **pypdf** | Extract text from uploaded resume PDFs |
| **python-dotenv** | Secure API key management |
| **Streamlit Community Cloud** | Free deployment, auto-updates on every git push |

---

## Project Structure

```
AI-Powered-Skill-Assessment/
├── app.py          → Streamlit UI + 3-stage flow logic
├── utils.py        → Groq API calls, PDF parsing, JSON handling  
├── prompts.py      → All LLM prompt templates
├── resources.py    → Curated resources for 35 skills, verified URLs
├── requirements.txt
├── .streamlit/
│   └── config.toml → Dark theme
└── README.md
```

---

## Run It Locally

**1. Clone**
```bash
git clone https://github.com/YR36/AI-Powered-Skill-Assessment.git
cd AI-Powered-Skill-Assessment
```

**2. Set up environment**
```bash
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

**3. Add your Groq API key**

Create a `.env` file:
```
GROQ_API_KEY=your_key_here
```
Get a free key at [console.groq.com](https://console.groq.com)

**4. Run**
```bash
streamlit run app.py
```

Opens at `http://localhost:8501`

---

## Sample Input & Output

**Input — Job Description:**
> Senior Backend Engineer. 5+ years Python, FastAPI, PostgreSQL, Docker, AWS. Will design scalable microservices and lead a team of 3.

**Input — Resume:**
> Yash Rana. 3 years experience. Python, FastAPI, PostgreSQL, React. Built a real-time fraud detection API handling 10k req/s. Deployed ML models with Flask and Docker.

**What happens:**
- Skills assessed: Python, FastAPI, PostgreSQL, Docker (overlap between JD and resume)
- Gap flagged: AWS (in JD, not on resume)
- 8 questions asked (2 per skill), calibrated to Senior level
- Scores revealed at the end: Python 7.5 · FastAPI 8.0 · PostgreSQL 6.0 · Docker 6.5

**Output — Readiness verdict:**
> You have solid fundamentals in Python and FastAPI but PostgreSQL and Docker need more depth at the senior level. AWS is a real gap for this role. Realistically 70% ready now — 85–90% achievable in 6–8 weeks with focused effort on query optimisation, Docker networking, and AWS core services.

---

## What's Curated (Not Hallucinated)

The learning plan pulls from a handpicked dictionary of 35 skills with verified resources from:
roadmap.sh · freeCodeCamp · official docs · Kaggle · fast.ai · MDN · Harvard CS50 · Exercism · LeetCode · HackerRank · The Odin Project · Hugging Face · MIT Missing Semester · ByteByteGo · and more.

No AI-generated URLs. Every link was verified before being added.

---
