from langserve import RemoteRunnable
from langchain_core.messages import AIMessage, HumanMessage
import requests

# response = requests.post("http://localhost:8000/agent/", json={
#   "input": "x-100機台未啟動怎麼辦？",
#   "chat_history": [
#     "你好，我叫何宏發",
#     "你好",
#     "我叫什麼名字?",
#     "你叫何宏發",
#     "很好，現在起請稱呼我為宏發。我有一個朋友叫 Cody。我想問x-100機台加工精度不佳該如何解決?",
#     "檢查刀具是否磨損，如有磨損應及時更換。確認冷卻液流量是否正常，過低的流量可能導致切削效果不佳。檢查伺服馬達是否正常運作，如有異常應及時聯繫維修人員。"
#   ],
#   "model": "gpt-3.5-turbo",
#   "model_params": {"temperature":0, "max_length":1000},
# })

response = requests.post("http://localhost:8000/agent/", json={
  "instruction": "你是一個廠務知識的聊天機器人，你擅長並只能根據Context和Chat History回答Question，以下是Context、Chat History和Question，請你只針對該Question回答。",
  "input": "x-100機台未啟動怎麼辦？",
  "chat_history": [],
  "model": "gpt-3.5-turbo",
  "model_params": {"temperature":0.1},
})

print(response.content.decode("utf-8"))
