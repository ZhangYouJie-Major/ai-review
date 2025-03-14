from flask import Flask
import yaml
import os

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), '../config/config.yml')
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def create_app():
    app = Flask(__name__)
    config = load_config()

    app.config['WEBHOOK_SECRET'] = config['webhook']['secret']
    app.config['WEBHOOK_PORT'] = config['webhook']['port']
    app.config['GITLAB_ACCESS_TOKEN'] = config['gitlab']['access_token']
    app.config['GITLAB_API_URL'] = config['gitlab']['api_url']
    app.config['DIFY_API_KEY'] = config['dify']['api_key']
    app.config['DIFY_API_URL'] = config['dify']['api_url']

    from .webhook import webhook_bp
    app.register_blueprint(webhook_bp)

    return app