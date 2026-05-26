SYSTEM_PROMPT = """You are OpenStudyLM, an intelligent AI study assistant.
You help students understand their study materials, answer questions clearly,
and generate exam-ready content. Always base your answers on the provided context.
Be clear and accurate."""

def build_qa_prompt(question: str, context: str, mode: str = "exam") -> str:
    mode_instructions = {
        "beginner": "Explain in very simple terms. Use analogies. Avoid jargon.",
        "exam": "Give a structured answer with key points, definitions, and examples. Be exam-ready.",
        "revision": "Give a very short bullet-point summary. Maximum 5 bullets."
    }
    instruction = mode_instructions.get(mode, mode_instructions["exam"])
    
    return f"""CONTEXT FROM STUDY MATERIALS:
{context}

STUDENT QUESTION:
{question}

INSTRUCTION: {instruction}

Answer the question using only the context above. Do not list sources at the end."""

def build_exam_pack_prompt(topics: str, context: str) -> str:
    return f"""You are creating an exam preparation pack for a student.

STUDY MATERIAL CONTEXT:
{context}

TOPICS TO COVER: {topics}

Generate a complete exam preparation pack with:
1. KEY CONCEPTS (5-8 bullet points)
2. IMPORTANT DEFINITIONS (5+ terms)
3. SHORT ANSWER QUESTIONS (5 questions with answers)
4. MCQs (5 questions with 4 options each, mark correct answer)
5. LONG ANSWER QUESTIONS (2-3 essay-style questions with outline answers)

Be thorough and exam-focused."""

def build_notebook_prompt(context: str) -> str:
    return f"""Analyze the following study material and create a structured topic-wise notebook.

STUDY MATERIAL:
{context}

Create a notebook with this structure:
## TOPIC 1: [Name]
### Subtopic 1.1
[explanation]
### Subtopic 1.2
[explanation]

## TOPIC 2: [Name]
...

Cover all major topics found in the material. Be comprehensive."""

def build_followup_prompt(question: str, answer: str) -> str:
    return f"""A student asked: "{question}"
The answer given was: "{answer[:500]}..."

Suggest 3 natural follow-up questions the student should ask next to deepen their understanding.
Return ONLY the 3 questions as a numbered list, nothing else."""
