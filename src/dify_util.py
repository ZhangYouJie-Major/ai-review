import requests
from flask import Flask, request, jsonify

DIFY_API_KEY = 'app-1HTsxnKAIvSP70c1GKVJhweW'
DIFY_API_URL = 'http://110.40.167.8/v1/chat-messages'


def call_dify_api(query):
    """
    调用 Dify API 进行 AI 审查
    """
    headers = {
        "Authorization": f"Bearer {DIFY_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "inputs": {},
        "query": query,
        "response_mode": "blocking",  # 使用阻塞模式
        "conversation_id": "",
        "user": "gitlab-bot"  # 用户标识符
    }

    response = requests.post(DIFY_API_URL, json=payload, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"调用 Dify API 失败: {response.status_code}, {response.text}")
        return None
