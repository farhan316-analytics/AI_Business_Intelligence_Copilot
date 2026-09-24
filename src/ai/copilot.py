import json
import ollama

from src.ai.tools import TOOLS


MODEL = "qwen2.5:7b"


SYSTEM_PROMPT = """
You are an AI Business Intelligence Copilot.

You answer business questions using verified analytics tools connected
to a PostgreSQL e-commerce analytics database.

IMPORTANT RULES:

1. Never invent business metrics.
2. When a question requires business data, use the appropriate tool.
3. Use the tool result as the source of truth.
4. Do not calculate important business metrics from memory.
5. Clearly distinguish verified facts from business interpretation.
6. If the available tools cannot answer the question, say so.
7. The current dataset does NOT contain product cost information.
   Therefore profit and profit margin are NOT available.
8. Do not invent profit, profit margin, costs, or other unavailable metrics.
9. When discussing monthly trends, remember that December 2011 is an
   incomplete month and should not be treated as a full-month decline.
10. Give concise, business-oriented explanations.
11. Do not infer causation from revenue or sales trends alone.
12. Never claim that seasonality, market conditions, customer behavior,
    marketing activity, competition, pricing, inventory, or other external
    factors caused a change unless the available data directly supports it.
13. If the data only shows that a metric increased or decreased, describe
    the observed change without claiming why it happened.
14. When a period is incomplete, explicitly state that the period is not
    directly comparable with complete periods.
15. Do not use phrases such as "indicating potential seasonal factors"
    unless the dataset contains sufficient repeated evidence to support
    a seasonality observation.
16. Prefer concise executive-style responses over long explanations.
17. For ranking or comparison questions, use a short Markdown bullet list
    instead of numbered paragraphs.
18. For decline or growth questions, show the percentage change and the
    relevant before-and-after revenue values when available.
19. Do not repeat the same metric in multiple sections.
20. For analytical questions, use at most three sections:
    **Key Findings**, **Business Insight**, and **Data Caveat**.
21. Keep the response under approximately 180 words unless the user
    explicitly asks for a detailed analysis.
22. For simple factual questions, do not create unnecessary sections.
23. Put the most important business finding first.
"""


def get_tool_definitions():
    """
    Convert our internal tool registry into Ollama tool definitions.
    """

    return [
        {
            "type": "function",
            "function": {
                "name": "business_kpis",
                "description": TOOLS["business_kpis"]["description"],
                "parameters": {
                    "type": "object",
                    "properties": {},
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "monthly_sales",
                "description": TOOLS["monthly_sales"]["description"],
                "parameters": {
                    "type": "object",
                    "properties": {},
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "country_performance",
                "description": TOOLS["country_performance"]["description"],
                "parameters": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Number of countries to return.",
                            "default": 20,
                        }
                    },
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "product_performance",
                "description": TOOLS["product_performance"]["description"],
                "parameters": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Number of products to return.",
                            "default": 20,
                        }
                    },
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "customer_performance",
                "description": TOOLS["customer_performance"]["description"],
                "parameters": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Number of customers to return.",
                            "default": 20,
                        }
                    },
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "top_products",
                "description": TOOLS["top_products"]["description"],
                "parameters": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Number of top products to return.",
                            "default": 10,
                        }
                    },
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "top_customers",
                "description": TOOLS["top_customers"]["description"],
                "parameters": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Number of top customers to return.",
                            "default": 10,
                        }
                    },
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "revenue_declines",
                "description": TOOLS["revenue_declines"]["description"],
                "parameters": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Number of revenue declines to return.",
                            "default": 5,
                        }
                    },
                },
            },
        },
    ]


def execute_tool(tool_name, arguments):
    if tool_name not in TOOLS:
        raise ValueError(f"Unknown tool: {tool_name}")

    function = TOOLS[tool_name]["function"]

    # Keep enough rows available for meaningful visualizations.
    # The AI can still use the first row to answer "which is highest?"
    if tool_name in [
        "country_performance",
        "product_performance",
        "customer_performance",
    ]:
        requested_limit = arguments.get("limit", 20)

        if requested_limit < 10:
            arguments["limit"] = 10

    return function(**arguments)

def format_copilot_response(answer):
    """
    Clean and standardize the AI response for the Streamlit UI.
    """

    if not answer:
        return answer

    # Remove excessive blank lines
    lines = answer.splitlines()

    cleaned_lines = []
    previous_blank = False

    for line in lines:

        line = line.strip()

        if not line:
            if not previous_blank:
                cleaned_lines.append("")

            previous_blank = True
            continue

        previous_blank = False
        cleaned_lines.append(line)

    answer = "\n".join(cleaned_lines).strip()

    # The dataset uses British pounds (GBP).
    # Normalize accidental dollar symbols from the LLM.
    answer = answer.replace("$", "£")

    return answer

def ask_copilot(question):
    """
    Send a business question to Qwen.

    Returns:
        {
            "answer": str,
            "tool_name": str or None,
            "tool_result": original verified result
        }
    """

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": question,
        },
    ]

    # First request: let Qwen decide whether to use a tool.
    response = ollama.chat(
        model=MODEL,
        messages=messages,
        tools=get_tool_definitions(),
    )

    messages.append(response["message"])

    tool_calls = response["message"].get("tool_calls", [])

    # No tool required
    if not tool_calls:

        return {
            "answer": response["message"]["content"],
            "tool_name": None,
            "tool_result": None,
        }

    tool_name = None
    tool_result = None

    # Execute requested tool
    for tool_call in tool_calls:

        tool_name = tool_call["function"]["name"]

        arguments = tool_call["function"].get(
            "arguments",
            {}
        )

        print(f"\n[AI TOOL SELECTED] {tool_name}")
        print(f"[TOOL ARGUMENTS] {arguments}")

        tool_result = execute_tool(
            tool_name,
            arguments,
        )

        # Convert DataFrame to JSON-friendly records
        if hasattr(tool_result, "to_dict"):

            tool_result_for_llm = tool_result.to_dict(
                orient="records"
            )

        else:

            tool_result_for_llm = tool_result

        messages.append(
            {
                "role": "tool",
                "content": json.dumps(
                    tool_result_for_llm,
                    default=str,
                ),
            }
        )

    # Second request: Qwen interprets verified results
    final_response = ollama.chat(
        model=MODEL,
        messages=messages,
    )

    answer = final_response["message"]["content"]

    answer = format_copilot_response(answer)

    return {
        "answer": answer,
        "tool_name": tool_name,
        "tool_result": tool_result,
    }


if __name__ == "__main__":

    print("=" * 70)
    print("AI BUSINESS INTELLIGENCE COPILOT")
    print("OLLAMA TOOL-CALLING TEST")
    print("=" * 70)

    question = "What is our total revenue?"

    print("\nQUESTION:")
    print(question)

    answer = ask_copilot(question)

    print("\nAI RESPONSE:")
    print(answer)

    print("\n" + "=" * 70)
    print("COPILOT TEST COMPLETE")
    print("=" * 70)