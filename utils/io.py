from langchain.memory import ChatMessageHistory
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
from typing import List


prompt = PromptTemplate(
  input_variables = ["input", "chat_history", "retrieved_document"],
   template="\
    你是一個場務知識的聊天機器人，你擅長根據Context和Chat History回答問題，\
    以下是Context、Chat History和Question，請你只針對該Question回答。\n\n\
    Context: {retrieved_document} \n\n\
    Chat History:\n{chat_history}\n\
    Question:{input} \n\
    Answer:",
)


class ModelParams(BaseModel):
  temperature: float
  max_length: int

class ChatRequest(BaseModel):
  input: str
  chat_history: List[str]
  model: str
  model_params: ModelParams

class VectorizedParams(BaseModel):
  chunk_size: int
  chunk_overlap: int


class FileUploadRequest(BaseModel):
  url: str
  file_name: str
  vectorize_params: VectorizedParams


class Output(BaseModel):
  output: str


def generate_chat_history(chat_history: List[str]):
  output = ""
  for i in range(len(chat_history)):
    if i % 2 == 0:
      output += "Human: " + chat_history[i] + "\n"
    else:
      output += "AI: " + chat_history[i] + "\n"
  return output

def generate_reference_output(docs):
  reference_output = "Reference:\n"
  for doc in docs:
    pdf_name = doc.metadata["source"].split("/")[-1]
    page = doc.metadata["page"]
    reference_output += f"{pdf_name} | Page {page}\n"
  return reference_output