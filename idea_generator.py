import os
import json
import re
from typing import Dict, Any, List, Tuple, Optional
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from pytrends.request import TrendReq

# ---------------------------
# Environment & Client
# ---------------------------
load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")
HF_MODEL = os.getenv("HF_MODEL", "mistralai/Mistral-7B-Instruct-v0.3")


def _get_client(model: Optional[str] = None) -> InferenceClient:
    """Returns an InferenceClient for the given model."""
    return InferenceClient(model or HF_MODEL, token=HF_TOKEN)


# ---------------------------
# Utility: Robust JSON parsing
# ---------------------------
def _extract_json(text: str) -> Optional[Any]:
    """Extract JSON from LLM responses."""
    if not text:
        return None

    # 1) Try fenced code block ```json ... ```
    fenced = re.findall(r"```json\s*(.*?)\s*```", text, flags=re.DOTALL | re.IGNORECASE)
    if fenced:
        for block in fenced:
            try:
                return json.loads(block)
            except Exception:
                pass

    # 2) Try any fenced block ```
    fenced_any = re.findall(r"```\s*(.*?)\s*```", text, flags=re.DOTALL)
    if fenced_any:
        for block in fenced_any:
            try:
                return json.loads(block)
            except Exception:
                pass

    # 3) Try full string as JSON
    try:
        return json.loads(text)
    except Exception:
        return None


# ---------------------------
# Core: Chat wrapper
# ---------------------------
def _chat(messages: List[Dict[str, str]],
          model: Optional[str] = None,
          max_tokens: int = 600,
          temperature: float = 0.7) -> str:
    """Calls Hugging Face chat_completion API and returns content string."""
    client = _get_client(model)
    resp = client.chat_completion(
        model=model or HF_MODEL,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature
    )
    content = resp.choices[0].message.content
    return content.replace("</|im_end|>", "").strip()


# ---------------------------
# Persona Builder
# ---------------------------
def build_persona(inputs: Dict[str, str],
                  temperature: float = 0.5) -> Tuple[Dict[str, Any], str]:
    """Return persona_dict and persona_text."""
    system = "You are a precise startup mentor. Always follow JSON output when asked."
    prompt = f"""
Create a concise user persona from the info below and return JSON only.

User Info:
- Background: {inputs.get('background','')}
- Skills: {inputs.get('skills','')}
- Interests: {inputs.get('interests','')}
- Past Experiences: {inputs.get('experiences','')}
- Current Position: {inputs.get('current_position','')}
- Goals/Motives: {inputs.get('goals','')}
- Future Aspirations: {inputs.get('aspirations','')}

JSON schema:
{{
  "summary": "2-3 sentence overview tailored to entrepreneurship",
  "strengths": ["bullet", "points"],
  "motivations": ["bullet", "points"],
  "risk_factors": ["bullet", "points"]
}}
Only return JSON.
"""
    raw = _chat(
        [{"role": "system", "content": system},
         {"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=500
    )
    data = _extract_json(raw) or {}
    persona = {
        "summary": data.get("summary") or "(summary unavailable)",
        "strengths": data.get("strengths") or [],
        "motivations": data.get("motivations") or [],
        "risk_factors": data.get("risk_factors") or [],
        "raw": raw
    }
    persona_text = (
        f"**Summary:** {persona['summary']}\n\n"
        f"**Key Strengths:**\n- " + "\n- ".join(persona["strengths"]) + "\n\n"
        f"**Motivations:**\n- " + "\n- ".join(persona["motivations"]) + "\n\n"
        f"**Risk Factors / Limitations:**\n- " + "\n- ".join(persona["risk_factors"])
    )
    return persona, persona_text


# ---------------------------
# Idea Generator
# ---------------------------
def generate_ideas(persona: Dict[str, Any],
                   industry: str,
                   problem: str,
                   n_ideas: int = 3,
                   temperature: float = 0.7) -> List[Dict[str, Any]]:
    """Generate structured startup ideas aligned to persona."""
    system = "You are a world-class startup ideation coach. Output JSON only when asked."
    prompt = f"""
Based on this persona and the context, produce {n_ideas} *niche* startup ideas that align with the user's skills and goals.
Persona Summary: {persona.get('summary','')}
Persona Strengths: {persona.get('strengths',[])}
Persona Motivations: {persona.get('motivations',[])}

Context:
- Industry: {industry}
- Problem Statement: {problem}

Return JSON list. Each idea must follow:
{{
  "title": "short catchy name",
  "elevator_pitch": "one sentence",
  "description": "3-5 sentences with solution, target user, and business model hint",
  "why_fit": "explain why this fits the persona",
  "competencies_required": ["skill/competency", "skill/competency", "skill/competency"]
}}
Only return JSON (list).
"""
    raw = _chat(
        [{"role": "system", "content": system},
         {"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=900
    )
    ideas = _extract_json(raw)
    return ideas if isinstance(ideas, list) else []


# ---------------------------
# Feasibility & Fit Mapping
# ---------------------------
def assess_feasibility(persona: Dict[str, Any],
                       ideas: List[Dict[str, Any]],
                       temperature: float = 0.4) -> List[Dict[str, Any]]:
    """Assess feasibility of ideas for the persona."""
    system = "You are a pragmatic startup coach. Output JSON only."
    prompt = f"""
Evaluate feasibility for the following ideas given this persona.

Persona:
- Summary: {persona.get('summary','')}
- Strengths: {persona.get('strengths',[])}
- Motivations: {persona.get('motivations',[])}
- Risk Factors: {persona.get('risk_factors',[])}

Ideas:
{json.dumps(ideas, ensure_ascii=False)}

For each idea, return:
{{
  "title": "exact title from the idea",
  "fit_score": 0-100,
  "matched_strengths": ["..."],
  "gaps": ["competency or resource gaps"],
  "ninety_day_plan": ["week-by-week action bullets for 90 days"]
}}
Return JSON list only.
"""
    raw = _chat(
        [{"role": "system", "content": system},
         {"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=1000
    )
    assessment = _extract_json(raw)
    return assessment if isinstance(assessment, list) else []


# ---------------------------
# Name Suggestions & Pitch
# ---------------------------
def suggest_names(idea_title: str,
                  keywords: str = "",
                  n: int = 8,
                  temperature: float = 0.9) -> List[str]:
    """Suggest brandable names for a startup idea."""
    system = "You are a brand naming expert. Output JSON only."
    prompt = f"""
Suggest {n} brandable names for a startup titled "{idea_title}".
Incorporate these keywords if useful: {keywords}.
Rules: short (≤ 12 chars when possible), easy to pronounce, .com plausibility.
Return JSON list of strings ONLY.
"""
    raw = _chat(
        [{"role": "system", "content": system},
         {"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=300
    )
    names = _extract_json(raw)
    return names if isinstance(names, list) else []


def generate_pitch(idea: Dict[str, Any],
                   tone: str = "crisp, benefit-led",
                   temperature: float = 0.6) -> str:
    """Generate an elevator pitch for a startup idea."""
    system = "You are a pitch-writing assistant."
    prompt = f"""
Write a 3–4 sentence elevator pitch in a {tone} tone for this idea:
{json.dumps(idea, ensure_ascii=False)}
"""
    return _chat(
        [{"role": "system", "content": system},
         {"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=250
    )


# ---------------------------
# Google Trends (optional)
# ---------------------------
def get_related_trends(topic: str):
    """Fetch related Google Trends queries."""
    try:
        pytrends = TrendReq()
        pytrends.build_payload([topic], timeframe='today 12-m')
        related = pytrends.related_queries()
        top = related.get(topic, {}).get("top")
        if top is not None:
            return top.head(5)
        return None
    except Exception as e:
        print("Trend Error:", e)
        return None