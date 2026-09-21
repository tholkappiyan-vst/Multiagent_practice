
! pip install langchain langchain-community langchain-google-genai

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
"""**multiagent - pdfreader**"""

from langchain_community.document_loaders import PyPDFLoader
from langchain.agents import create_agent

from langchain_community.document_loaders import PyPDFLoader
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langchain.tools import tool

loader = PyPDFLoader("/content/Tholkappiyan_Resume.pdf")
documents = loader.load()

@tool
def read_pdf(question: str) -> str:
    """ answer a question using the PDF content."""
    text = "\n".join(abc.page_content for abc in documents)
    return text

agent = create_agent(
    model=llm,
    tools=[read_pdf],
    system_prompt="""
    You are a PDF reader agent.
    Ue the read_pdf tool to find information from the pdf
    Answer only using information from the PDF,
    If the answer is not available in the PDF , say that you don't have that information.
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
