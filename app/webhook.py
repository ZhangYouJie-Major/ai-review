from flask import Blueprint, request, jsonify
from .gitlab_utils import handle_merge_request
from .utils import verify_signature

webhook_bp = Blueprint('webhook', __name__)

@webhook_bp.route('/webhook', methods=['POST'])
def webhook():
    signature = request.headers.get('X-Gitlab-Token')
    if not verify_signature(request.data, signature):
        return jsonify({'error': 'Invalid signature'}), 403

    event = request.headers.get('X-Gitlab-Event')
    data = request.json

    if event == 'Merge Request Hook':
        handle_merge_request(data)

    return jsonify({'status': 'success'}), 200