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

"""**multi -agent - placement assistant without db**"""

@tool
def list_company(question: str) -> str:
    """ list out the companies names which will comes to college campus"""
    names = ['amazon', 'acenture', 'paypal', 'tcs', 'wipro', 'triology', 'servicenow', 'infosys']
    return str(names)

@tool
def apply_company(question: str) -> str:
    """apply the placement drive for the candidate"""
    message = 'congrats vst! your application is submitted to' + question
    return message

agent = create_agent(
    model=llm,
    tools=[list_company, apply_company],
    system_prompt="""
    you are the placemnet assistant for the college student
    you can use the suitable tool for it
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
