! pip install langchain langchain-community langchain-google-genai

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langchain.tools import tool

import os

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise RuntimeError("Set the GOOGLE_API_KEY environment variable before running this script.")
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model='gemini-3.5-flash-lite',
    temperature=0,
)

import re

@tool
def add(question: str) -> str:
    """Calculates the addition of numbers extracted from a string."""
    total_sum = sum([int(num) for num in re.findall(r'\d+', question)])
    return str(total_sum)

@tool
def multiply(question: str) -> str:
    """Calculates the multipy of numbers extracted from a string."""
    total_sum = sum([int(num) for num in re.findall(r'\d+', question)])
    return str(total_sum)

agent = create_agent(
    model=llm,
    tools=[add, multiply],
    system_prompt="""
    you are the mathematician give the answer based on the user prompt
    use suitable tool, dont change the tool's output even if it is wrong
    """
)

question = input("Ask something")
result = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": question,
            }
        ]
    }
)
answer = result["messages"][-1].content

if isinstance(answer, list):
    answer = "\n".join(item["text"] for item in answer)

print("\n" + "="*60)
print(question)
print("\n" + "="*60)
print(answer)
