"""
API pour le moteur IA hybride de Léa
Expose les fonctionnalités d'intelligence artificielle avancées
"""

from flask import Blueprint, request, jsonify
import asyncio
import logging
from typing import Dict, Any

from ..ai.hybrid_ai_engine import HybridAIEngine

logger = logging.getLogger(__name__)

# Configuration des clés API (à déplacer vers les variables d'environnement en production)
CHATGPT_API_KEY = "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"
DEEPSEEK_API_KEY = "sk-bdd815f97ae84c79a6b6fe02d4730646"

# Initialiser le moteur IA hybride
ai_engine = HybridAIEngine(CHATGPT_API_KEY, DEEPSEEK_API_KEY)

ai_api = Blueprint('ai_api', __name__)

def run_async(coro):
    """Helper pour exécuter des coroutines dans Flask"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(coro)

@ai_api.route('/health', methods=['GET'])
def health_check():
    """Vérification de l'état de l'API IA"""
    return jsonify({
        "status": "healthy",
        "service": "Léa AI Engine",
        "version": "1.0.0",
        "capabilities": [
            "intelligent_code_generation",
            "comprehensive_code_analysis",
            "intelligent_debugging", 
            "smart_optimization",
            "hybrid_reasoning"
        ]
    })

@ai_api.route('/generate-code', methods=['POST'])
def generate_code():
    """
    Génération de code intelligente
    
    Body:
    {
        "prompt": "Description du code à générer",
        "language": "python",
        "complexity": "medium",
        "use_parallel": true
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'prompt' not in data:
            return jsonify({
                "success": False,
                "error": "Le champ 'prompt' est requis"
            }), 400
        
        prompt = data['prompt']
        language = data.get('language', 'python')
        complexity = data.get('complexity', 'medium')
        use_parallel = data.get('use_parallel', True)
        
        # Validation des paramètres
        valid_languages = ['python', 'javascript', 'java', 'cpp', 'csharp', 'go', 'rust']
        valid_complexity = ['simple', 'medium', 'complex']
        
        if language not in valid_languages:
            return jsonify({
                "success": False,
                "error": f"Langage non supporté. Langages disponibles: {valid_languages}"
            }), 400
        
        if complexity not in valid_complexity:
            return jsonify({
                "success": False,
                "error": f"Complexité invalide. Niveaux disponibles: {valid_complexity}"
            }), 400
        
        # Génération de code via le moteur IA hybride
        result = run_async(ai_engine.intelligent_code_generation(
            prompt, language, complexity, use_parallel
        ))
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Erreur génération code: {e}")
        return jsonify({
            "success": False,
            "error": "Erreur interne du serveur",
            "details": str(e)
        }), 500

@ai_api.route('/analyze-code', methods=['POST'])
def analyze_code():
    """
    Analyse complète de code
    
    Body:
    {
        "code": "Code source à analyser",
        "language": "python",
        "include_asu": true
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'code' not in data:
            return jsonify({
                "success": False,
                "error": "Le champ 'code' est requis"
            }), 400
        
        code = data['code']
        language = data.get('language', 'python')
        include_asu = data.get('include_asu', True)
        
        if not code.strip():
            return jsonify({
                "success": False,
                "error": "Le code ne peut pas être vide"
            }), 400
        
        # Analyse via le moteur IA hybride
        result = run_async(ai_engine.comprehensive_code_analysis(
            code, language, include_asu
        ))
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Erreur analyse code: {e}")
        return jsonify({
            "success": False,
            "error": "Erreur interne du serveur",
            "details": str(e)
        }), 500

@ai_api.route('/debug-code', methods=['POST'])
def debug_code():
    """
    Débogage intelligent de code
    
    Body:
    {
        "code": "Code avec problème",
        "error_message": "Message d'erreur (optionnel)",
        "language": "python"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'code' not in data:
            return jsonify({
                "success": False,
                "error": "Le champ 'code' est requis"
            }), 400
        
        code = data['code']
        error_message = data.get('error_message', '')
        language = data.get('language', 'python')
        
        # Débogage via le moteur IA hybride
        result = run_async(ai_engine.intelligent_debugging(
            code, error_message, language
        ))
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Erreur débogage: {e}")
        return jsonify({
            "success": False,
            "error": "Erreur interne du serveur",
            "details": str(e)
        }), 500

@ai_api.route('/optimize-code', methods=['POST'])
def optimize_code():
    """
    Optimisation intelligente de code
    
    Body:
    {
        "code": "Code à optimiser",
        "language": "python",
        "optimization_goals": ["performance", "readability"]
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'code' not in data:
            return jsonify({
                "success": False,
                "error": "Le champ 'code' est requis"
            }), 400
        
        code = data['code']
        language = data.get('language', 'python')
        optimization_goals = data.get('optimization_goals', ['performance'])
        
        # Validation des objectifs d'optimisation
        valid_goals = ['performance', 'readability', 'security', 'size']
        invalid_goals = [g for g in optimization_goals if g not in valid_goals]
        
        if invalid_goals:
            return jsonify({
                "success": False,
                "error": f"Objectifs invalides: {invalid_goals}. Objectifs disponibles: {valid_goals}"
            }), 400
        
        # Optimisation via le moteur IA hybride
        result = run_async(ai_engine.smart_optimization(
            code, language, optimization_goals
        ))
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Erreur optimisation: {e}")
        return jsonify({
            "success": False,
            "error": "Erreur interne du serveur",
            "details": str(e)
        }), 500

@ai_api.route('/explain-code', methods=['POST'])
def explain_code():
    """
    Explication de code
    
    Body:
    {
        "code": "Code à expliquer",
        "language": "python"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'code' not in data:
            return jsonify({
                "success": False,
                "error": "Le champ 'code' est requis"
            }), 400
        
        code = data['code']
        language = data.get('language', 'python')
        
        # Explication via ChatGPT (plus adapté pour l'explication)
        result = ai_engine.chatgpt.explain_code(code, language)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Erreur explication: {e}")
        return jsonify({
            "success": False,
            "error": "Erreur interne du serveur",
            "details": str(e)
        }), 500

@ai_api.route('/design-architecture', methods=['POST'])
def design_architecture():
    """
    Conception d'architecture système
    
    Body:
    {
        "requirements": "Exigences du système",
        "scale": "medium"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'requirements' not in data:
            return jsonify({
                "success": False,
                "error": "Le champ 'requirements' est requis"
            }), 400
        
        requirements = data['requirements']
        scale = data.get('scale', 'medium')
        
        valid_scales = ['small', 'medium', 'large', 'enterprise']
        if scale not in valid_scales:
            return jsonify({
                "success": False,
                "error": f"Échelle invalide. Échelles disponibles: {valid_scales}"
            }), 400
        
        # Conception via DeepSeek (plus adapté pour l'architecture)
        result = ai_engine.deepseek.system_architecture_design(requirements, scale)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Erreur conception architecture: {e}")
        return jsonify({
            "success": False,
            "error": "Erreur interne du serveur",
            "details": str(e)
        }), 500

@ai_api.route('/solve-problem', methods=['POST'])
def solve_problem():
    """
    Résolution de problèmes complexes
    
    Body:
    {
        "problem_description": "Description du problème",
        "context": {}
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'problem_description' not in data:
            return jsonify({
                "success": False,
                "error": "Le champ 'problem_description' est requis"
            }), 400
        
        problem_description = data['problem_description']
        context = data.get('context', {})
        
        # Résolution via DeepSeek (spécialisé dans le raisonnement complexe)
        result = ai_engine.deepseek.complex_problem_solving(problem_description, context)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Erreur résolution problème: {e}")
        return jsonify({
            "success": False,
            "error": "Erreur interne du serveur",
            "details": str(e)
        }), 500

@ai_api.route('/engine-stats', methods=['GET'])
def get_engine_stats():
    """Statistiques du moteur IA hybride"""
    try:
        stats = ai_engine.get_engine_stats()
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Erreur stats moteur: {e}")
        return jsonify({
            "success": False,
            "error": "Erreur interne du serveur",
            "details": str(e)
        }), 500

@ai_api.route('/supported-languages', methods=['GET'])
def get_supported_languages():
    """Liste des langages de programmation supportés"""
    return jsonify({
        "success": True,
        "languages": [
            {
                "code": "python",
                "name": "Python",
                "features": ["syntax_analysis", "code_generation", "optimization", "debugging"]
            },
            {
                "code": "javascript",
                "name": "JavaScript",
                "features": ["syntax_analysis", "code_generation", "optimization", "debugging"]
            },
            {
                "code": "java",
                "name": "Java",
                "features": ["code_generation", "optimization", "debugging"]
            },
            {
                "code": "cpp",
                "name": "C++",
                "features": ["code_generation", "optimization", "debugging"]
            },
            {
                "code": "csharp",
                "name": "C#",
                "features": ["code_generation", "optimization", "debugging"]
            },
            {
                "code": "go",
                "name": "Go",
                "features": ["code_generation", "optimization", "debugging"]
            },
            {
                "code": "rust",
                "name": "Rust",
                "features": ["code_generation", "optimization", "debugging"]
            }
        ],
        "total_languages": 7,
        "asu_supported": ["python", "javascript"],
        "ai_supported": ["python", "javascript", "java", "cpp", "csharp", "go", "rust"]
    })

@ai_api.route('/capabilities', methods=['GET'])
def get_capabilities():
    """Capacités complètes de Léa"""
    return jsonify({
        "success": True,
        "ai_capabilities": {
            "code_generation": {
                "description": "Génération de code intelligente multi-langage",
                "engines": ["ChatGPT", "DeepSeek"],
                "complexity_levels": ["simple", "medium", "complex"],
                "parallel_processing": True
            },
            "code_analysis": {
                "description": "Analyse complète avec ASU, sécurité et performance",
                "engines": ["ChatGPT", "DeepSeek", "ASU"],
                "features": ["syntax_analysis", "security_scan", "performance_analysis", "quality_metrics"]
            },
            "debugging": {
                "description": "Débogage intelligent avec suggestions de correction",
                "engines": ["ChatGPT", "DeepSeek"],
                "features": ["error_detection", "fix_suggestions", "root_cause_analysis"]
            },
            "optimization": {
                "description": "Optimisation multi-critères du code",
                "engines": ["ChatGPT", "DeepSeek"],
                "goals": ["performance", "readability", "security", "size"]
            },
            "architecture_design": {
                "description": "Conception d'architecture système complète",
                "engines": ["DeepSeek"],
                "scales": ["small", "medium", "large", "enterprise"]
            }
        },
        "unique_features": [
            "Arbre Syntaxique Universel (ASU) breveté",
            "Système Zero Trust intégré",
            "Auto-pentest automatique",
            "IA hybride multi-moteurs",
            "Optimisation intelligente des coûts IA"
        ],
        "competitive_advantages": [
            "Seul assistant avec ASU universel",
            "Sécurité Zero Trust native",
            "Analyse de vulnérabilités automatique",
            "Combinaison optimale de plusieurs IAs",
            "Architecture brevetable unique"
        ]
    })

