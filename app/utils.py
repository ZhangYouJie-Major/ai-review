from flask import current_app

def verify_signature(data, signature):
    if not current_app.config['WEBHOOK_SECRET']:
        return True
    return current_app.config['WEBHOOK_SECRET'] == signature