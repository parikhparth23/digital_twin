import json
import os
from pypdf import PdfReader
from dotenv import load_dotenv
from google import genai

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

BASE_DIR = Path(__file__).resolve().parent.parent

SUMMARY_PATH = BASE_DIR / "resources" / "summary.txt"
RESUME_PATH = BASE_DIR / "resources" / "resume.pdf"
load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

MODEL = "gemini-3.1-flash-lite"

def load_summary():
    return SUMMARY_PATH.read_text(encoding="utf-8")


def load_resume():
    reader = PdfReader(RESUME_PATH)

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    return text


summary = load_summary()
resume = load_resume()

def judge(question: str, answer: str):

    prompt = f"""
You are an expert evaluator for an AI Digital Twin.

Your job is to evaluate the assistant's answer.

==========================
GROUND TRUTH
==========================

Summary:

{summary}

Resume:

{resume}

==========================
QUESTION
==========================

{question}

==========================
ASSISTANT ANSWER
==========================

{answer}

==========================
SCORING
==========================

Score each category from 1 to 10.

Scoring rubric:

10 = Perfect. No factual errors, no unsupported claims, directly answers the question.
9 = Excellent. Tiny wording issues only.
8 = Good. Minor omissions or slightly incomplete.
7 = Acceptable. Some missing details or one unsupported statement.
5-6 = Major issues but still somewhat useful.
1-4 = Mostly incorrect, hallucinated, or failed the task.

A score of 10 should be rare.
If you are unsure whether a claim is supported by the resume, deduct points.

Faithfulness

Compare every factual claim in the answer against the resume and summary.

Deduct points for:

- facts not present in the resume
- invented metrics
- invented technologies
- invented companies
- invented timelines
- assumptions

Do NOT reward plausible facts.

If even one unsupported factual claim exists,
the maximum Faithfulness score is 8.

Relevance

Does every paragraph help answer the user's question?

Deduct points if:

- the answer is unnecessarily long
- it includes unrelated experience
- it misses important requested information

Persona

The assistant should always behave as Parth's AI Digital Twin.

Deduct points if it:

- speaks as ChatGPT
- gives generic AI advice
- breaks character
- discusses topics outside Parth's career

Refusal

If the question is in scope:

Score 10.

If the question is outside scope:

Score based on whether the refusal was correct.

Incorrectly answering an out-of-scope question should receive 1.

Return ONLY valid JSON.

For every score below 10,
explain exactly why points were deducted.

Mention the unsupported claim or omission.

Example:

{{
  "overall": 9,
  "faithfulness": 8,
  "relevance": 10,
  "persona": 10,
  "refusal": 10,
  "reason": "Claimed 90% scoring accuracy, which is not found in the resume."
}}

Return JSON only.
"""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
    )

    # print("=" * 80)
    # print(repr(response.text))
    # print("=" * 80)


    text = response.text

    if not text:
        raise Exception("Gemini returned an empty response.")

    text = text.strip()

    text = text.replace("```json", "")
    text = text.replace("```", "")
    text = text.strip()

    return json.loads(text)