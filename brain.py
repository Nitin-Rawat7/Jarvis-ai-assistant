from groq import Groq

GROQ_API_KEY="your_api_key"

client = Groq(api_key=GROQ_API_KEY)

def ask_jarvis(prompt: str, history: list = []) -> str:

    system_prompt = """You are JARVIS — a professional, intelligent AI assistant.
Rules:
- For actions (opening apps, websites, files, playing songs): reply in MAX 5 words only. Examples: 'Done.' or 'Opening YouTube now.' or 'Playing song.' or 'Screenshot taken.'
- NEVER say a video is playing or buffering — just confirm the action briefly
- For questions: reply in 2-4 sentences
- Never repeat the question
- Be direct and straight to the point
- No long introductions"""

    messages = [{"role": "system", "content": system_prompt}]

    for entry in history[-6:]:
        if entry.get("role") in ("user", "assistant"):
            messages.append({
                "role": entry["role"],
                "content": entry["content"]
            })

    messages.append({"role": "user", "content": prompt})

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            max_tokens=50,        # ← reduced — actions need only 5 words
            temperature=0.3,      # ← lower — less hallucination
        )
        return response.choices[0].message.content

    except Exception as e:
        return f"Error: {str(e)}"