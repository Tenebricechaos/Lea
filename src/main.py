import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from src.models.user import db
from src.routes.user import user_bp
from src.routes.ast_api import ast_bp
from src.routes.security_api import security_bp
from src.routes.ai_api import ai_api
from src.routes.payments_api import payments_api

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Configuration CORS pour permettre les requêtes cross-origin
from flask_cors import CORS
CORS(app)

app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(ast_bp, url_prefix='/api/ast')
app.register_blueprint(security_bp, url_prefix='/api/security')
app.register_blueprint(ai_api, url_prefix='/api/ai')
app.register_blueprint(payments_api, url_prefix='/api/payments')

# uncomment if you need to use database
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return {
        "service": "Léa - Assistant de Codage Révolutionnaire",
        "version": "1.0.0",
        "status": "operational",
        "apis": {
            "user": "/api",
            "ast": "/api/ast",
            "security": "/api/security",
            "ai": "/api/ai",
            "payments": "/api/payments"
        },
        "features": [
            "Arbre Syntaxique Universel (ASU)",
            "Système Zero Trust",
            "Auto-pentest automatique",
            "IA hybride (ChatGPT + DeepSeek)",
            "Paiements Stripe intégrés",
            "Analyse de code multi-langage",
            "Génération de code intelligente",
            "Optimisation et débogage avancés"
        ],
        "competitive_advantages": [
            "Seul assistant avec ASU universel breveté",
            "Sécurité Zero Trust native",
            "IA hybride pour résultats optimaux",
            "Système de paiement intégré",
            "Architecture scalable et extensible"
        ]
    }

@app.route('/health')
def health():
    return {
        "status": "healthy",
        "service": "Léa Backend",
        "components": {
            "ast_engine": "operational",
            "security_system": "operational",
            "ai_engine": "operational", 
            "payment_system": "operational"
        }
    }

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
