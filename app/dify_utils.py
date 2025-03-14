import requests
from flask import current_app


def ai_review(file_changes_markdown: str) -> str:
    headers = {
        "Authorization": f"Bearer {current_app.config['DIFY_API_KEY']}",
        "Content-Type": "application/json"
    }
    payload = {
        "inputs": {},
        "query": file_changes_markdown,
        "response_mode": "blocking",
        "conversation_id": "",
        "user": "gitlab-bot"
    }

    response = requests.post(current_app.config['DIFY_API_URL'], json=payload, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"调用 Dify API 失败: {response.status_code}, {response.text}")
        return ''
