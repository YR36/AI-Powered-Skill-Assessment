import streamlit as st
from utils import (
    extract_text_from_pdf,
    parse_jd_and_resume,
    generate_question,
    score_answer,
    generate_learning_plan
)

st.set_page_config(
    page_title="Skill Assessment Agent",
    page_icon="🧠",
    layout="wide"
)

st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: 'Inter', 'Segoe UI', sans-serif;
}
[data-testid="stChatMessage"] {
    border-radius: 14px;
    padding: 6px 10px;
    margin-bottom: 6px;
}
.stButton > button {
    border-radius: 10px;
    font-weight: 600;
    letter-spacing: 0.3px;
    transition: all 0.2s ease;
    border: none;
}
.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 15px rgba(255,255,255,0.08);
}
[data-testid="stMetric"] {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 14px;
    padding: 18px;
    text-align: center;
}
[data-testid="stExpander"] {
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    margin-bottom: 10px;
}
[data-testid="stAlert"] {
    border-radius: 12px;
}
hr {
    border-color: rgba(255,255,255,0.08);
    margin: 28px 0;
}
[data-testid="stProgress"] > div {
    border-radius: 99px;
}
[data-testid="stChatInput"] > div {
    border-radius: 14px;
    border: 1px solid rgba(255,255,255,0.15);
}
.plan-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 12px;
}
</style>
""", unsafe_allow_html=True)


# ── Reaction helpers ─────────────────────────────────────────────────
def score_emoji(score: float) -> str:
    if score >= 8: return "🟢"
    if score >= 5: return "🟡"
    return "🔴"

def score_label(score: float) -> str:
    if score >= 8: return "Strong"
    if score >= 6: return "Decent"
    if score >= 4: return "Needs Work"
    return "Weak"

def transition_message(skill: str, score: float, next_skill: str = None) -> str:
    label = score_label(score)
    emoji = score_emoji(score)
    base = f"{emoji} **{skill}** wrapped up — scored **{score}/10** ({label})."
    if next_skill:
        return base + f"\n\nAlright, moving on to **{next_skill}**. Let's see how you do here. 👇"
    return base + "\n\nThat's the last skill. Putting together your plan now..."

def welcome_message(parsed: dict, questions_per_skill: int) -> str:
    name = parsed.get("candidate_name", "there")
    title = parsed.get("job_title", "the role")
    seniority = parsed.get("seniority_level", "mid")
    skills = parsed.get("skills_to_assess", [])
    suggest = parsed.get("skills_to_suggest", [])
    summary = parsed.get("skill_overlap_summary", "")

    skills_str = " → ".join([f"**{s}**" for s in skills])
    suggest_str = ", ".join(suggest) if suggest else "None"

    return f"""👋 Hey **{name}**! I've gone through your profile for **{title}**.

{summary}

Here's the plan:
- 🎯 **Skills I'll assess** (on your resume + needed by JD): {skills_str}
- 📌 **Gaps I'll flag** (in JD but not on your resume): {suggest_str}
- 📊 **{questions_per_skill} questions per skill**, starting easy and getting harder based on how you answer
- 🧠 Seniority level: **{seniority.upper()}** — questions are calibrated to this

I'll react to your answers honestly — no sugarcoating, but no roasting either.

Ready? Let's start with **{skills[0]}**. 👇"""


# ── Session state ────────────────────────────────────────────────────
def init_state():
    defaults = {
        "stage": "input",
        "parsed": None,
        "current_skill_index": 0,
        "skill_histories": {},
        "skill_scores": {},
        "current_question": None,
        "questions_per_skill": 2,
        "resume_text": "",
        "chat_log": [],
        "waiting_for_answer": False,
        "assessment_complete": False,
        "learning_plan": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()


def get_current_skill():
    skills = st.session_state.parsed.get("skills_to_assess", [])
    idx = st.session_state.current_skill_index
    return skills[idx] if idx < len(skills) else None

def add_message(role: str, content: str):
    st.session_state.chat_log.append({"role": role, "content": content})

def compute_skill_score(history: list) -> float:
    if not history: return 0
    return round(sum(h["score"] for h in history) / len(history), 1)


# ── STAGE: INPUT ─────────────────────────────────────────────────────
if st.session_state.stage == "input":
    st.title("🧠 AI Skill Assessment Agent")
    st.markdown(
        "Drop in a **Job Description** and your **Resume**. "
        "I'll figure out what actually matters, quiz you on it, "
        "and give you a real learning plan — not a generic one."
    )
    st.divider()

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.subheader("📋 Job Description")
        jd_text = st.text_area(
            "Paste the full JD here",
            height=320,
            placeholder="We are looking for a Senior Backend Engineer with 5+ years experience in Python, FastAPI, PostgreSQL, Docker, AWS..."
        )

    with col2:
        st.subheader("📄 Your Resume")
        tab1, tab2 = st.tabs(["📎 Upload PDF", "✏️ Paste Text"])
        with tab1:
            uploaded_file = st.file_uploader("Upload resume as PDF", type=["pdf"])
        with tab2:
            resume_text_input = st.text_area(
                "Or paste plain text",
                height=270,
                placeholder="Yash Rana\nSoftware Engineer, 2 years experience\nSkills: Python, React, PostgreSQL\nProjects: Built an ML pipeline for fraud detection..."
            )

    st.divider()
    col_a, col_b = st.columns([2, 1])
    with col_a:
        questions_count = st.slider(
            "⚡ Questions per skill — fewer is faster, more is more accurate",
            min_value=2, max_value=4, value=2
        )
    with col_b:
        st.metric("Estimated Time", f"~{questions_count * 4} min", "based on 4 skills")

    if st.button("🚀 Start Assessment", type="primary", use_container_width=True):
        if not jd_text.strip():
            st.error("Please paste a Job Description.")
            st.stop()

        resume_final = ""
        if uploaded_file:
            resume_final = extract_text_from_pdf(uploaded_file)
        elif resume_text_input.strip():
            resume_final = resume_text_input.strip()
        else:
            st.error("Please provide a resume — upload PDF or paste text.")
            st.stop()

        with st.spinner("Analysing JD and resume... hang tight ⚡"):
            parsed = parse_jd_and_resume(jd_text, resume_final)

        if "error" in parsed:
            st.error(f"Parsing failed: {parsed.get('raw', parsed['error'])}")
            st.stop()

        if not parsed.get("skills_to_assess"):
            st.warning("Couldn't find overlapping skills between JD and resume. Try adding more detail to your resume.")
            st.stop()

        st.session_state.parsed = parsed
        st.session_state.resume_text = resume_final
        st.session_state.questions_per_skill = questions_count
        st.session_state.stage = "assessing"

        add_message("assistant", welcome_message(parsed, questions_count))
        st.rerun()


# ── STAGE: ASSESSING ─────────────────────────────────────────────────
elif st.session_state.stage == "assessing":

    parsed = st.session_state.parsed
    skills = parsed.get("skills_to_assess", [])
    seniority = parsed.get("seniority_level", "mid")
    projects = parsed.get("relevant_projects", [])
    resume_ctx = st.session_state.resume_text[:1200]

    # Progress bar
    total_q = len(skills) * st.session_state.questions_per_skill
    answered_q = sum(len(v) for v in st.session_state.skill_histories.values())
    progress = answered_q / total_q if total_q > 0 else 0
    current_skill = get_current_skill()

    st.title("🧠 Skill Assessment")
    st.progress(
        progress,
        text=f"Skill {min(st.session_state.current_skill_index + 1, len(skills))} of {len(skills)} — {answered_q}/{total_q} questions done"
    )
    st.divider()

    # Render chat
    for msg in st.session_state.chat_log:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Assessment complete — generate plan
    if st.session_state.assessment_complete:
        with st.spinner("Generating your personalised learning plan... 🔍"):
            plan = generate_learning_plan(
                candidate_name=parsed.get("candidate_name", "Candidate"),
                job_title=parsed.get("job_title", "the role"),
                seniority=seniority,
                skill_scores=st.session_state.skill_scores,
                skills_to_suggest=parsed.get("skills_to_suggest", [])
            )
        st.session_state.learning_plan = plan
        st.session_state.stage = "plan"
        st.rerun()

    # Generate next question
    if current_skill and not st.session_state.waiting_for_answer:
        history = st.session_state.skill_histories.get(current_skill, [])
        q_count = len(history)

        if q_count < st.session_state.questions_per_skill:
            with st.spinner(f"Thinking of a question on **{current_skill}**..."):
                question = generate_question(
                    skill=current_skill,
                    seniority=seniority,
                    history=history,
                    resume_context=resume_ctx,
                    projects=projects
                )
            st.session_state.current_question = question
            st.session_state.waiting_for_answer = True

            prefix = f"**[{current_skill.upper()} — Q{q_count + 1}/{st.session_state.questions_per_skill}]**\n\n"
            add_message("assistant", prefix + question)
            st.rerun()

        else:
            # Skill done
            avg = compute_skill_score(st.session_state.skill_histories.get(current_skill, []))
            st.session_state.skill_scores[current_skill] = {
                "average_score": avg,
                "questions_asked": q_count
            }

            st.session_state.current_skill_index += 1
            next_skill = get_current_skill() if st.session_state.current_skill_index < len(skills) else None
            st.session_state.waiting_for_answer = False

            if st.session_state.current_skill_index >= len(skills):
                st.session_state.assessment_complete = True
                add_message("assistant", transition_message(current_skill, avg, None))
            else:
                add_message("assistant", transition_message(current_skill, avg, next_skill))

            st.rerun()

    # Chat input
    if st.session_state.waiting_for_answer:
        user_input = st.chat_input("Your answer...")
        if user_input:
            add_message("user", user_input)

            with st.spinner("Scoring..."):
                result = score_answer(
                    skill=current_skill,
                    question=st.session_state.current_question,
                    answer=user_input,
                    seniority=seniority
                )

            score = result.get("score", 5)
            reaction = result.get("reaction", "")
            justification = result.get("justification", "")

            if current_skill not in st.session_state.skill_histories:
                st.session_state.skill_histories[current_skill] = []

            st.session_state.skill_histories[current_skill].append({
                "question": st.session_state.current_question,
                "answer": user_input,
                "score": score
            })

            emoji = score_emoji(score)
            feedback = f"{reaction}\n\n{justification}"
            add_message("assistant", feedback)
            st.session_state.waiting_for_answer = False
            st.rerun()


# ── STAGE: PLAN ──────────────────────────────────────────────────────
elif st.session_state.stage == "plan":

    plan = st.session_state.learning_plan
    parsed = st.session_state.parsed

    st.title("📋 Your Personalised Learning Plan")
    st.divider()

    if "error" in plan:
        st.error("Plan generation failed. Raw output:")
        st.code(plan.get("raw", ""))
        st.stop()

    # ── Top Summary ──
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("👤 Candidate", parsed.get("candidate_name", "—"))
    col2.metric("🎯 Target Role", parsed.get("job_title", "—"))
    col3.metric("📊 Match Score", f"{plan.get('overall_match_score', '—')}%")
    col4.metric("🏁 Seniority", parsed.get("seniority_level", "—").upper())

    st.divider()
    st.info(f"💬 **{plan.get('summary', '')}**")

    # ── Skill Score Cards ──
    st.subheader("🎯 Assessed Skills")
    scores = st.session_state.skill_scores
    if scores:
        cols = st.columns(len(scores))
        for i, (skill, data) in enumerate(scores.items()):
            avg = data['average_score']
            emoji = score_emoji(avg)
            label = score_label(avg)
            cols[i].metric(
                label=f"{emoji} {skill.upper()}",
                value=f"{avg}/10",
                delta=label
            )

    # ── Skills to Work On (gaps from JD not on resume) ──
    suggest = plan.get("suggested_to_add", [])
    if suggest:
        st.divider()
        st.subheader("📌 Skills to Add to Your Profile")
        st.caption("These were in the JD but not on your resume — worth picking up for this role.")
        for item in suggest:
            with st.expander(f"**{item.get('skill', '').upper()}** — ⏱ {item.get('time_estimate', '?')}"):
                st.markdown(f"**Why it matters:** {item.get('why_add', '')}")
                for r in item.get("resources", []):
                    st.markdown(f"- [{r.get('title', '')}]({r.get('url', '')}) — *{r.get('type', '')}*")

    # ── Priority Improvements ──
    st.divider()
    st.subheader("🚀 Where to Focus First")
    for item in plan.get("priority_skills", []):
        score = item.get("current_score", 0)
        emoji = score_emoji(score)
        status = item.get("status", "")

        with st.expander(
            f"{emoji} **{item.get('skill', '').upper()}** — "
            f"{item.get('current_score', '?')}/10 → {item.get('target_score', '?')}/10 "
            f"| ⏱ {item.get('time_estimate', '?')} | `{status}`"
        ):
            st.markdown(f"**Why it matters for this role:** {item.get('why_important', '')}")
            st.markdown(f"**How to approach it:** {item.get('approach', '')}")
            st.markdown("**Resources:**")
            for r in item.get("resources", []):
                st.markdown(f"- [{r.get('title', '')}]({r.get('url', '')}) — *{r.get('type', '')}*")

    # ── Week by Week ──
    st.divider()
    st.subheader("📅 Week-by-Week Plan")
    weeks = plan.get("week_by_week_plan", [])
    if weeks:
        cols = st.columns(min(len(weeks), 3))
        for i, week in enumerate(weeks):
            with cols[i % 3]:
                st.markdown(f"""
<div class="plan-card">
<strong>{week.get('week', '')}</strong><br/>
{week.get('focus', '')}<br/><br/>
<em>🎯 {week.get('goal', '')}</em>
</div>
""", unsafe_allow_html=True)

    # ── Readiness verdict ──
    st.divider()
    st.success(f"🏁 **Readiness Verdict:** {plan.get('realistic_readiness', '')}")

    if st.button("🔄 Start New Assessment", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()