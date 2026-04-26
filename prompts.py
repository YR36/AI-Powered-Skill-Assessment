def get_parsing_prompt(jd: str, resume: str) -> str:
    return f"""You are an expert technical recruiter and skill analyst.

Analyze the Job Description and Resume below. Return ONLY a valid JSON object, no explanation, no markdown.

Job Description:
{jd}

Resume:
{resume}

Return this exact JSON structure:
{{
  "job_title": "extracted job title",
  "seniority_level": "junior|mid|senior|lead",
  "years_experience_required": 0,
  "candidate_name": "name from resume",
  "candidate_experience_years": 0,
  "relevant_projects": ["brief project description max 15 words each, max 3 projects"],
  "skills_to_assess": ["max 4 skills that appear in BOTH JD requirements AND candidate resume/experience"],
  "skills_to_suggest": ["skills required by JD but NOT found in resume - these are real gaps"],
  "skill_overlap_summary": "one sentence on how well resume matches JD"
}}

RULES:
- skills_to_assess: ONLY skills the candidate has claimed AND the JD requires. Max 4. Most critical first.
- skills_to_suggest: Skills the JD needs but the resume doesn't show. These won't be tested, just flagged.
- If overlap is less than 4 skills, only return what genuinely overlaps. Do not invent.
- relevant_projects: pick projects most relevant to the JD role"""


def get_question_prompt(skill: str, seniority: str, history: list, resume_context: str, projects: list) -> str:
    history_text = ""
    if history:
        history_text = "\n".join([
            f"Q: {h['question']}\nA: {h['answer']}\nScore: {h['score']}/10"
            for h in history
        ])

    level_guide = {
        "junior": "Focus on fundamentals and basic concepts. Avoid system design. Simple practical scenarios.",
        "mid": "Mix fundamentals with real-world application. Include debugging and tradeoff questions.",
        "senior": "Architecture decisions, tradeoffs, scalability, production issues. No basic questions.",
        "lead": "System-wide thinking, cross-team impact, technical vision, mentoring scenarios."
    }

    projects_text = "\n".join([f"- {p}" for p in projects]) if projects else "Not specified"

    thresholds = {
    "junior": {"escalate": 7, "maintain": 4},
    "mid":    {"escalate": 8, "maintain": 5},
    "senior": {"escalate": 8, "maintain": 6},
    "lead":   {"escalate": 9, "maintain": 7},
    }
    t = thresholds.get(seniority, thresholds["mid"])

    escalation_rule = "This is the first question — start foundational."
    if history:
        last_score = history[-1]["score"]
        if last_score >= t["escalate"]:
            escalation_rule = f"Last score was {last_score}/10 — escalate difficulty."
        elif last_score >= t["maintain"]:
            escalation_rule = f"Last score was {last_score}/10 — maintain level, different angle."
        else:
            escalation_rule = f"Last score was {last_score}/10 — simplify, try a different approach."
    return f"""You are a sharp, experienced technical interviewer. You have personality — direct, honest, occasionally witty, but always professional.

Skill being assessed: {skill}
Seniority level required: {seniority}
Depth guidance: {level_guide.get(seniority, level_guide['mid'])}
Escalation rule: {escalation_rule}

Candidate's resume context: {resume_context[:800]}
Candidate's relevant projects:
{projects_text}

Previous Q&A for this skill:
{history_text if history_text else "None — this is the first question."}

RULES:
- Ask ONE question only. No preamble, no "Great question!", no explanation.
- Where relevant, tie the question to one of the candidate's actual projects listed above.
- Never repeat a question already asked.
- The question should be specific, not vague. Bad: "Tell me about Python." Good: "In your ML pipeline project, how did you handle memory efficiently when processing large datasets?"
- Do NOT include the answer or hints.

Return ONLY the question text. Nothing else."""


def get_scoring_prompt(skill: str, question: str, answer: str, seniority: str) -> str:
    return f"""You are a strict but fair technical interviewer scoring an answer.

Skill: {skill}
Seniority expected: {seniority}
Question: {question}
Candidate's answer: {answer}

Scoring guide:
- 9-10: Exceptional. Complete, accurate, shows deep understanding and nuance.
- 7-8: Good. Core concept correct, minor gaps in depth or edge cases.
- 5-6: Partial. Right direction but missing key details or accuracy issues.
- 3-4: Weak. Vague, partially incorrect, or surface-level only.
- 0-2: Incorrect or no real understanding demonstrated.

Return ONLY a valid JSON object:
{{
  "score": 7,
  "reaction": "Short human reaction (1 sentence). Vary your tone — can be encouraging, honest, or direct. Examples: 'Solid understanding of the core concept.' / 'You got the what but missed the why.' / 'That is exactly the right mental model.' / 'Partially there — the GIL part was right, but the asyncio angle was off.'",
  "justification": "What specifically they got right AND what was missing or could be deeper. Be concrete, not generic. 2 sentences max.",
  "follow_up_needed": true
}}

Be honest. A vague answer is 4-5, not 7. Penalise buzzword answers with no substance."""


def get_learning_plan_prompt(
    candidate_name: str,
    job_title: str,
    seniority: str,
    skill_scores: dict,
    skills_to_suggest: list,
    resources_map: dict
) -> str:
    scores_text = "\n".join([
        f"- {skill}: {data['average_score']}/10 ({data['questions_asked']} questions)"
        for skill, data in skill_scores.items()
    ])

    suggest_text = "\n".join([f"- {s}" for s in skills_to_suggest]) if skills_to_suggest else "None identified"

    resources_text = ""
    for skill, resources in resources_map.items():
        resources_text += f"\n{skill}:\n"
        for r in resources:
            resources_text += f"  - {r['title']} | {r['url']} | {r['type']} | {r['time']}\n"

    return f"""You are a senior engineering mentor creating a personalised, realistic learning plan.

Candidate: {candidate_name}
Target Role: {job_title} ({seniority} level)

Assessed Skills (candidate claimed + JD required):
{scores_text}

Skills to suggest working on (in JD but not on resume):
{suggest_text}

Curated resources available:
{resources_text}

Create a focused, honest, realistic plan. Do not over-promise timelines.

Return ONLY a valid JSON object:
{{
  "summary": "2-3 sentence honest assessment. Reference actual scores. Be direct — not corporate-speak.",
  "overall_match_score": 72,
  "priority_skills": [
    {{
      "skill": "skill name",
      "current_score": 5,
      "target_score": 8,
      "status": "needs_improvement|completely_missing|strong",
      "why_important": "one concrete sentence on why this matters for THIS specific role",
      "time_estimate": "e.g. 3-4 weeks",
      "approach": "one sentence on HOW to approach learning this specifically",
      "resources": [
        {{"title": "resource title", "url": "url", "type": "type"}}
      ]
    }}
  ],
  "suggested_to_add": [
    {{
      "skill": "skill name",
      "why_add": "why this matters for the role",
      "time_estimate": "realistic time",
      "resources": [{{"title": "title", "url": "url", "type": "type"}}]
    }}
  ],
  "week_by_week_plan": [
    {{"week": "Week 1-2", "focus": "specific focus area", "goal": "concrete measurable outcome"}}
  ],
  "realistic_readiness": "e.g. 65% ready now. Realistically 85% in 8 weeks with consistent effort."
}}"""