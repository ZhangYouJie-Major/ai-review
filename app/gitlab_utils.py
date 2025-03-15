import requests
from flask import current_app
from .dify_utils import ai_review
import gitlab


def get_gitlab_client():
    """
    初始化并返回 GitLab 客户端
    """
    return gitlab.Gitlab(
        url=current_app.config['GITLAB_API_URL'],
        private_token=current_app.config['GITLAB_ACCESS_TOKEN']
    )


def get_merge_request_changes(project_id, merge_request_id):
    """
    获取 Merge Request 的变更文件
    """
    gl = get_gitlab_client()
    project = gl.projects.get(project_id)
    merge_request = project.mergerequests.get(merge_request_id)
    changes = merge_request.changes()
    return changes['changes']


def add_merge_request_comment(project_id, merge_request_id, comment):
    """
    向 Merge Request 添加评论
    """
    if not comment:
        raise ValueError("Comment cannot be empty")

    if isinstance(comment, dict):
        comment = str(comment)

    if len(comment) > 1000000:
        comment = comment[:1000000]  # 截断过长的评论

    gl = get_gitlab_client()
    project = gl.projects.get(project_id)
    merge_request = project.mergerequests.get(merge_request_id)
    merge_request.notes.create({'body': comment})
    print("评论添加成功！")


def handle_merge_request(data):
    merge_request = data['object_attributes']
    project_id = merge_request['target_project_id']
    merge_request_id = merge_request['iid']  # 注意：GitLab API 使用的是 iid 而不是 id
    source_branch = merge_request['source_branch']
    target_branch = merge_request['target_branch']
    title = merge_request['title']
    description = merge_request['description']

    # 检查 Merge Request 的状态和操作
    if merge_request['state'] != 'opened' or merge_request['action'] not in ['open', 'update', 'reopen']:
        print(f"Ignoring Merge Request with state: {merge_request['state']}, action: {merge_request['action']}")
        return

    # 获取变更的文件列表
    changes = get_merge_request_changes(project_id, merge_request_id)
    file_changes = extract_changes(changes)
    file_changes_markdown = generate_markdown(file_changes)

    # 调用 AI 审查
    comment = ai_review(file_changes_markdown)

    # 添加评论
    add_merge_request_comment(project_id, merge_request_id, comment['answer'])


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
