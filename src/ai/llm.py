import ollama


SYSTEM_PROMPT = """
You are an AI Business Intelligence Copilot.

Your job is to help business users understand e-commerce
performance using verified analytics produced by the system.

Important rules:

1. Never invent business metrics.
2. Never claim a metric exists if it has not been provided.
3. Clearly distinguish facts from interpretation.
4. If the available data cannot answer a question, say so.
5. Do not claim that profit or profit margin is available because
   the current dataset does not contain product cost information.
6. Be concise but useful.
7. When discussing changes over time, consider whether the period
   is complete or incomplete.
8. Highlight unusual or potentially anomalous results when relevant.
9. Give business-oriented explanations rather than merely repeating
   raw numbers.
"""


def ask_llm(question):

    response = ollama.chat(
        model="qwen2.5:7b",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": question
            }
        ]
    )

    return response["message"]["content"]


if __name__ == "__main__":

    print("=" * 70)
    print("AI BUSINESS INTELLIGENCE COPILOT")
    print("OLLAMA + QWEN CONNECTION TEST")
    print("=" * 70)

    question = "What is business intelligence?"

    print("\nQUESTION:")
    print(question)

    answer = ask_llm(question)

    print("\nAI RESPONSE:")
    print(answer)

    print("\n" + "=" * 70)
    print("OLLAMA CONNECTION TEST COMPLETE")
    print("=" * 70)