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


message = """you are a medical field assistant to a doctor, the doctor provides you with a query he receives from the patient and you have to respond to the doctor based on the context provided along the patient query. if the context and the patient query doesn't align, suggest the doctor to recheck the context.
<rules>
1. If the query is outside of the medical field, Respond with "I don't know", don't elaborate further!
2. If the query and the context doesn't align, Respond with "I don't know", don't elaborate further!
3. If the Query is basic greeting, greet politely and introduce yourself as a doctor's assitant
</rules>
Strictly adhere to these rules while answering the query.
<context>
    {context}
</context>
<query>
    {query}
</query>
"""

greeting_message = """
you are a medical field assistant to a doctor. Thus, greet the doctor in polite and professional manner. Ask him to mention his dilema or problem.
"""

reform_query = """Given a chat history and the latest user question \
which might reference context in the chat history, formulate a standalone question \
which can be understood without the chat history. Do NOT answer the question, \
just reformulate it if needed and otherwise return it as is.
Do not provide additonal information in the response.
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