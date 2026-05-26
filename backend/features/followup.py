from rag.llm_client import ask_llama
from rag.prompt_templates import build_followup_prompt

def get_followup_questions(question: str, answer: str) -> list[str]:
    prompt = build_followup_prompt(question, answer)
    response = ask_llama(prompt)
    
    # Parse numbered list
    lines = [l.strip() for l in response.split("\n") if l.strip()]
    questions = []
    for line in lines:
        # Remove numbering like "1." "1)" etc.
        if line and line[0].isdigit():
            cleaned = line.split(".", 1)[-1].strip()
            cleaned = cleaned.split(")", 1)[-1].strip()
            if cleaned:
                questions.append(cleaned)
    
    return questions[:3]  # max 3
