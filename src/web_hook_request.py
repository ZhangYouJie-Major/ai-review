from flask import Flask, request, jsonify
import requests
import hmac
import hashlib

app = Flask(__name__)

# 你的 GitLab Webhook Secret Token
WEBHOOK_SECRET = 'dXMLYnDkuTNPxUkFaPQUCPQtdymUFDJfniRIrOGpvpJ'
gitlab_access_token = 'glpat-2g7XKkWycSjiH7R2rLiK'


@app.route('/webhook', methods=['POST'])
def webhook():
    # 验证 Webhook 请求
    signature = request.headers.get('X-Gitlab-Token')
    if not verify_signature(request.data, signature):
        return jsonify({'error': 'Invalid signature'}), 403

    event = request.headers.get('X-Gitlab-Event')
    data = request.json

    if event == 'Merge Request Hook':
        handle_merge_request(data)

    return jsonify({'status': 'success'}), 200


def verify_signature(data, signature):
    # 使用 HMAC 验证签名
    if not WEBHOOK_SECRET:
        return True  # 如果没有设置 Secret Token，跳过验证
    return WEBHOOK_SECRET == signature


def handle_merge_request(data):
    # 处理 Merge Request 信息
    merge_request = data['object_attributes']
    #项目标识
    project_id = merge_request['target_project_id']
    #merge request id
    merge_request_id = merge_request['id']
    #原分支
    source_branch = merge_request['source_branch']
    # 目标分支
    target_branch = merge_request['target_branch']
    # 合并主题
    title = merge_request['title']
    # 描述
    description = merge_request['description']

    # 获取变更的文件列表
    changes_url = f'http://127.0.0.1:8200/api/v4/projects/{project_id}/merge_requests/{merge_request_id}/changes'
    headers = {'PRIVATE-TOKEN': gitlab_access_token}
    response = requests.get(changes_url, headers=headers)
    changes = response.json()

    # 提取变更的文件
    changed_files = changes['changes']

    file_changes = extract_changes(changed_files)
    file_changes_markdown = generate_markdown(file_changes)
    print(file_changes_markdown)
    # 调用 AI Review 功能
    # ai_review(title, description, changed_files)


def extract_changes(changes):
    """
    从 GitLab Merge Request 数据中提取变更的文件和内容
    """
    file_changes = []

    for change in changes:
        file_info = {
            'file_path': change.get('new_path') or change.get('old_path'),
            'diff': change.get('diff'),
            'change_type': 'modified'
        }

        if change.get('new_file'):
            file_info['change_type'] = 'added'
        elif change.get('deleted_file'):
            file_info['change_type'] = 'deleted'

        file_changes.append(file_info)

    return file_changes


def generate_markdown(file_changes) -> str:
    """
    将 Git 变更转化为 Markdown 格式
    """
    markdown_content = "### Git Merge 变更详情\n\n"

    for change in file_changes:
        file_path = change['file_path']
        diff_content = change['diff']
        change_type = change['change_type']

        # 添加文件标题
        markdown_content += f"#### 文件: `{file_path}` ({change_type})\n"

        # 添加 diff 内容
        markdown_content += "```diff\n"
        markdown_content += diff_content
        markdown_content += "\n```\n\n"

    return markdown_content


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000)
