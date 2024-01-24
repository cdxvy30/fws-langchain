from typing import List
from dotenv import load_dotenv
import os
from operator import itemgetter

from fastapi import FastAPI, Body
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import OpenAIEmbeddings
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.tools.retriever import create_retriever_tool
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_openai import ChatOpenAI
from langchain import hub, HuggingFaceHub
from langchain.agents import create_openai_functions_agent
from langchain.agents import AgentExecutor
from langchain.pydantic_v1 import BaseModel, Field
from langchain_core.messages import BaseMessage
from langchain.chains.question_answering import load_qa_chain
from langchain_core.runnables import RunnablePassthrough
from langserve import add_routes
from langchain_core.output_parsers import StrOutputParser
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory

from src.utils.io import Input, Output, ChatRequest

load_dotenv()

# 1. Load PDF
loader = PyPDFLoader('./sample/機台型號_ x-100.pdf')
text_spilter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=300)
splits = loader.load_and_split(text_splitter=text_spilter)
# embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
embeddings = HuggingFaceEmbeddings()
vectorstore = FAISS.from_documents(splits, embeddings)
# retriever = vectorstore.as_retriever()

# 2. Design prompting
prompt = PromptTemplate(
   input_variables = ["input", "chat_history", "retrieved_document"],
   template="\
    你是一個場務知識的聊天機器人，你擅長根據Context和Chat History回答問題，\
    以下是Context、Chat History和問題，請你只針對該問題回答。\n\n\
    Context: {retrieved_document} \n\n\
    Chat History:\n{chat_history}\n\n\
    Question:{input} \n\
    Answer:",
)

# 3. Define LLM and chain
llm = HuggingFaceHub(
  repo_id="mistralai/Mixtral-8x7B-Instruct-v0.1",
  model_kwargs={"temperature":0.8, "max_length":1000},
)
chain = LLMChain(
   llm=llm,
   prompt=prompt,
)

def concatenate_docs(docs):
    return "\n\n".join(doc.page_content.replace("\n", "") for doc in docs)

app = FastAPI(
  title="LangChain Server",
  version="1.0",
  description="A simple API server using LangChain's Runnable interfaces",
)

@app.post("/query/")
async def agent(request: ChatRequest) -> str:
  """Handle a request."""
  # Retrieve document from retriever
  retrieved_document = concatenate_docs(vectorstore.similarity_search(request.input, k=2))

  # Convert chat history to string
  chat_history = ""
  for i in range(len(request.chat_history)):
    if i % 2 == 0:
      chat_history += "Human: " + request.chat_history[i] + "\n"
    else:
      chat_history += "AI: " + request.chat_history[i] + "\n"

  # Run the chain
  res = chain.run({
      "input": request.input,
      "chat_history": chat_history,
      "retrieved_document": retrieved_document
  })
  print(res)
  return res


if __name__ == "__main__":
  import uvicorn

  uvicorn.run(app, host="localhost", port=8000)