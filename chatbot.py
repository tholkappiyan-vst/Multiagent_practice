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

"""**chatbot**  """

! pip install pypdf

import gradio as gr
from pypdf import PdfReader
from langchain_google_genai import ChatGoogleGenerativeAI

reader = PdfReader("ABC Restaurant.pdf")
restaurant_info = ""

for page in reader.pages:
    text = page.extract_text()
    if text:
        restaurant_info += text + "\n"


def chatbot(message, history):
    prompt = f""" you are a restaurant customer support assistant
    use the following restaurant information
    to answer the customer 's question.

    Restaurant information :
    {restaurant_info}

    customer Question :
    {message}

    Answer the customer clearly and politely
    if the information is not available in the
    restaurant information , say that you don't
    have that information .
    """
    response = llm.invoke(prompt)
    return response.content


demo = gr.ChatInterface(
    fn=chatbot,
    title="ABC Restaurant Chatbot",
    description="Ask anything about ABC Restaurant",
)

demo.launch()
