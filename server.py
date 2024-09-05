#server code for classification LLM
from fastapi import FastAPI
from pydantic import BaseModel

from dotenv import load_dotenv
import os
load_dotenv()
os.environ['GROQ_API_KEY'] = os.getenv('GROQ_API_KEY')

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.prompts import MessagesPlaceholder

from langchain_groq import ChatGroq

llm = ChatGroq(
    model="llama-3.1-70b-versatile",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    # other params...
)


message =    """
    You are a customer service assistant for Manjushree Finance. Your goal is to help customers with their queries by providing accurate, polite, and helpful information based strictly on the company's knowledge base, which includes operations, financial products, policies, and regulations.

    - If the retrieved data does not provide a definitive answer, respond with: "I'm unable to provide a clear answer at the moment. Please feel free to contact our customer support for further assistance."
    - Always maintain a friendly and professional tone.
    - Provide relevant URLs or references if applicable, based on the knowledge base.
    - Avoid assumptions or speculative responses.

    {context}

    Customer Question: {query}

    """

greeting_message = """
you are a customer service assistant for Manjushree Finance. Thus, greet the customer in polite and professional manner
"""




app = FastAPI()

class Data(BaseModel):
    query: str
    context: str

@app.post("/respond")
async def respond(data: Data):
    prompt = PromptTemplate.from_template(message)
    chain = prompt | llm
    resp = chain.invoke({
        'context' : data.context,
        'query' : data.query
    })
    return {
        'response' : resp.content
    }

@app.get('/greeting')
async def greeting():

    
    prompt = PromptTemplate.from_template(greeting_message)
    chain = prompt | llm
    resp = chain.invoke({})

    return {
        'response' : resp.content
    }

@app.post("/reform_query")
async def reform_query(data):
    chat_history = data.chat_history
    query = data.query

    updated_chat_history = []

    for human, ai in chat_history.items():
        updated_chat_history.extend([HumanMessage(human), AIMessage(ai)])
    
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", reform_query),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    chain = prompt | llm
    resp = chain.invoke({"chat_history":updated_chat_history, "input":query})

    print(resp.content)

    return resp.content