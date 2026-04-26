import os
import json
import pypdf
import io
from groq import Groq
from dotenv import load_dotenv
from prompts import (
    get_parsing_prompt,
    get_question_prompt,
    get_scoring_prompt,
    get_learning_plan_prompt
)
from resources import get_resources_for_skill

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"


def call_groq(prompt: str, temperature: float = 0.3) -> str:
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=2000,
    )
    return response.choices[0].message.content.strip()


def safe_parse_json(text: str) -> dict:
    try:
        text = text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text.strip())
    except Exception as e:
        return {"error": str(e), "raw": text}


def extract_text_from_pdf(uploaded_file) -> str:
    try:
        pdf_bytes = uploaded_file.read()
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text.strip()
    except Exception as e:
        return f"Error reading PDF: {e}"


def parse_jd_and_resume(jd: str, resume: str) -> dict:
    prompt = get_parsing_prompt(jd, resume)
    raw = call_groq(prompt, temperature=0.1)
    return safe_parse_json(raw)


def generate_question(skill: str, seniority: str, history: list, resume_context: str, projects: list) -> str:
    prompt = get_question_prompt(skill, seniority, history, resume_context, projects)
    return call_groq(prompt, temperature=0.6)


def score_answer(skill: str, question: str, answer: str, seniority: str) -> dict:
    prompt = get_scoring_prompt(skill, question, answer, seniority)
    raw = call_groq(prompt, temperature=0.1)
    return safe_parse_json(raw)


def generate_learning_plan(
    candidate_name: str,
    job_title: str,
    seniority: str,
    skill_scores: dict,
    skills_to_suggest: list
) -> dict:
    all_skills = list(skill_scores.keys()) + skills_to_suggest
    resources_map = {skill: get_resources_for_skill(skill) for skill in all_skills}
    prompt = get_learning_plan_prompt(
        candidate_name, job_title, seniority,
        skill_scores, skills_to_suggest, resources_map
    )
    raw = call_groq(prompt, temperature=0.4)
    return safe_parse_json(raw)