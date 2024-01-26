"""
Description: Entrypoint for the application.
"""

from dotenv import load_dotenv
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from utils.io import Output, ChatRequest, FileUploadRequest, generate_chat_history, generate_reference_output 
from ingest import ingest_docs
from chain import get_chain
from upload import upload_to_gcs

load_dotenv()


app = FastAPI(
  title="LangChain Server",
  description="A simple API server using LangChain's Runnable interfaces",
)


app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
  expose_headers=["*"],
)


db = None

def initialize_db():
  global db
  db = ingest_docs()


@app.post("/agent/")
async def agent(request: ChatRequest) -> str:
  """Handle a request."""
  chat_history = generate_chat_history(request.chat_history)

  docs = db.similarity_search(request.input, k=2)

  reference_output = generate_reference_output(docs)

  chain = get_chain(request.model, chain_type="stuff")

  model_output = chain.run({
    "input": request.input,
    "chat_history": chat_history,
    "retrieved_document": docs
  })

  res = model_output + "\n\n" + reference_output

  return res


@app.post("/feedback/")
async def feedback(request):
  """Handle feedbacks"""
  print(request)
  return {"output": "OK"}


@app.post("/upload_file/")
async def upload_file(request: FileUploadRequest):
  """Handle files upload to GCS"""
  upload_to_gcs(project_id=os.getenv("GOOGLE_CLOUD_PROJECT_ID"), url=request.url, file_name=request.file_name)
  
  global db
  db = ingest_docs()
  
  return {"message": "file uploaded successfully"}


if __name__ == "__main__":
  import uvicorn

  initialize_db()

  uvicorn.run(app, host="localhost", port=8000)