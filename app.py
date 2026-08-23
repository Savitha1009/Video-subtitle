import os
from flask import Flask
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_app(config_object="config.config.Config"):
    app = Flask(__name__)
    app.config.from_object(config_object)
    
    # Register Blueprints
    from routes.auth import auth_bp
    from routes.video import video_bp
    from routes.ui import ui_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(video_bp, url_prefix='/api')
    app.register_blueprint(ui_bp)
    
    return app

if __name__ == '__main__':
    app = create_app()
    port = app.config.get('PORT', 5000)
    app.run(host='0.0.0.0', port=port, debug=True)
