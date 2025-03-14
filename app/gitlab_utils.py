import requests
from flask import current_app


def handle_merge_request(data):
    merge_request = data['object_attributes']
    project_id = merge_request['target_project_id']
    merge_request_id = merge_request['id']
    source_branch = merge_request['source_branch']
    target_branch = merge_request['target_branch']
    title = merge_request['title']
    description = merge_request['description']

    changes_url = f"{current_app.config['GITLAB_API_URL']}/projects/{project_id}/merge_requests/{merge_request_id}/changes"
    headers = {'PRIVATE-TOKEN': current_app.config['GITLAB_ACCESS_TOKEN']}
    response = requests.get(changes_url, headers=headers)
    changes = response.json()

    changed_files = changes['changes']
    file_changes = extract_changes(changed_files)
    file_changes_markdown = generate_markdown(file_changes)

    comment = ai_review(file_changes_markdown)
    add_merge_request_comment(project_id, merge_request_id, comment)


def extract_changes(changes):
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
    markdown_content = "### Git Merge 变更详情\n\n"
    for change in file_changes:
        file_path = change['file_path']
        diff_content = change['diff']
        change_type = change['change_type']

        markdown_content += f"#### 文件: `{file_path}` ({change_type})\n"
        markdown_content += "```diff\n"
        markdown_content += diff_content
        markdown_content += "\n```\n\n"
    return markdown_content


def add_merge_request_comment(project_id, merge_request_iid, comment):
    gitlab_api_url = f"{current_app.config['GITLAB_API_URL']}/projects/{project_id}/merge_requests/{merge_request_iid}/notes"
    headers = {
        "PRIVATE-TOKEN": current_app.config['GITLAB_ACCESS_TOKEN'],
        "Content-Type": "application/json"
    }
    payload = {"body": comment}
    response = requests.post(gitlab_api_url, json=payload, headers=headers)

    if response.status_code == 201:
        print("评论添加成功！")
    else:
        print(f"评论添加失败: {response.status_code}, {response.text}")
