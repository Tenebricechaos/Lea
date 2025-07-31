"""
API REST pour l'Arbre Syntaxique Universel de Léa
Fournit les endpoints pour parser, analyser et manipuler le code via l'ASU.
"""

from flask import Blueprint, request, jsonify
from typing import Dict, Any, Optional
import traceback

from src.parsers.base_parser import parser_registry, parse_code, detect_language
from src.parsers.python_parser import PythonParser
from src.parsers.javascript_parser import JavaScriptParser
from src.models.ast_universal import UniversalSyntaxTree

# Création du blueprint
ast_bp = Blueprint('ast', __name__)

# Enregistrement des parsers
parser_registry.register_parser(PythonParser())
parser_registry.register_parser(JavaScriptParser())


@ast_bp.route('/parse', methods=['POST'])
def parse_source_code():
    """
    Parse du code source et retourne l'ASU
    
    Body JSON:
    {
        "source_code": "code source à parser",
        "language": "langage (optionnel)",
        "file_path": "chemin du fichier (optionnel)"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'source_code' not in data:
            return jsonify({
                'error': 'Le champ source_code est requis'
            }), 400
        
        source_code = data['source_code']
        language = data.get('language')
        file_path = data.get('file_path')
        
        # Parse le code
        ust = parse_code(source_code, language, file_path)
        
        # Retourne l'ASU en JSON
        return jsonify({
            'success': True,
            'ast': ust.to_json(),
            'metadata': ust.metadata
        })
        
    except ValueError as e:
        return jsonify({
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'error': f'Erreur interne: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500


@ast_bp.route('/detect-language', methods=['POST'])
def detect_source_language():
    """
    Détecte le langage de programmation du code source
    
    Body JSON:
    {
        "source_code": "code source à analyser",
        "file_path": "chemin du fichier (optionnel)"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'source_code' not in data:
            return jsonify({
                'error': 'Le champ source_code est requis'
            }), 400
        
        source_code = data['source_code']
        file_path = data.get('file_path')
        
        # Détecte le langage
        detected_language = detect_language(source_code, file_path)
        
        return jsonify({
            'success': True,
            'detected_language': detected_language,
            'supported_languages': parser_registry.list_supported_languages(),
            'supported_extensions': parser_registry.list_supported_extensions()
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Erreur lors de la détection: {str(e)}'
        }), 500


@ast_bp.route('/analyze', methods=['POST'])
def analyze_ast():
    """
    Analyse un ASU et retourne des informations détaillées
    
    Body JSON:
    {
        "source_code": "code source",
        "language": "langage (optionnel)",
        "analysis_type": "type d'analyse (functions, variables, complexity, etc.)"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'source_code' not in data:
            return jsonify({
                'error': 'Le champ source_code est requis'
            }), 400
        
        source_code = data['source_code']
        language = data.get('language')
        analysis_type = data.get('analysis_type', 'all')
        
        # Parse le code
        ust = parse_code(source_code, language)
        
        # Effectue l'analyse
        analysis_result = _analyze_ust(ust, analysis_type)
        
        return jsonify({
            'success': True,
            'analysis': analysis_result,
            'metadata': ust.metadata
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Erreur lors de l\'analyse: {str(e)}'
        }), 500


@ast_bp.route('/convert', methods=['POST'])
def convert_language():
    """
    Convertit du code d'un langage vers un autre (fonctionnalité future)
    
    Body JSON:
    {
        "source_code": "code source",
        "from_language": "langage source",
        "to_language": "langage cible"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'source_code' not in data:
            return jsonify({
                'error': 'Le champ source_code est requis'
            }), 400
        
        # Pour l'instant, retourne une réponse indiquant que la fonctionnalité est en développement
        return jsonify({
            'success': False,
            'message': 'La conversion entre langages est en cours de développement',
            'supported_conversions': []
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Erreur lors de la conversion: {str(e)}'
        }), 500


@ast_bp.route('/languages', methods=['GET'])
def get_supported_languages():
    """Retourne la liste des langages supportés"""
    try:
        return jsonify({
            'success': True,
            'languages': parser_registry.list_supported_languages(),
            'extensions': parser_registry.list_supported_extensions(),
            'parsers': {
                lang: parser_registry.get_parser(lang).get_language_info()
                for lang in parser_registry.list_supported_languages()
            }
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Erreur lors de la récupération des langages: {str(e)}'
        }), 500


@ast_bp.route('/health', methods=['GET'])
def health_check():
    """Vérification de l'état de l'API ASU"""
    return jsonify({
        'success': True,
        'service': 'Léa ASU API',
        'version': '1.0.0',
        'status': 'healthy',
        'parsers_loaded': len(parser_registry.list_supported_languages())
    })


def _analyze_ust(ust: UniversalSyntaxTree, analysis_type: str) -> Dict[str, Any]:
    """Analyse un ASU et retourne des informations détaillées"""
    from src.models.ast_universal import NodeType
    
    analysis = {}
    
    if analysis_type in ['all', 'functions']:
        # Analyse des fonctions
        functions = ust.get_nodes_by_type(NodeType.FUNCTION_DECLARATION)
        analysis['functions'] = {
            'count': len(functions),
            'details': [
                {
                    'name': func.get_attribute('name', 'anonymous'),
                    'parameters': func.get_attribute('parameters', []),
                    'line': func.source_range.start.line if func.source_range else None,
                    'is_async': func.get_attribute('is_async', False)
                }
                for func in functions
            ]
        }
    
    if analysis_type in ['all', 'variables']:
        # Analyse des variables
        variables = ust.get_nodes_by_type(NodeType.VARIABLE_DECLARATION)
        analysis['variables'] = {
            'count': len(variables),
            'details': [
                {
                    'name': var.get_attribute('name', 'unknown'),
                    'type': var.get_attribute('type'),
                    'kind': var.get_attribute('kind'),  # const, let, var pour JS
                    'line': var.source_range.start.line if var.source_range else None
                }
                for var in variables
            ]
        }
    
    if analysis_type in ['all', 'classes']:
        # Analyse des classes
        classes = ust.get_nodes_by_type(NodeType.CLASS_DECLARATION)
        analysis['classes'] = {
            'count': len(classes),
            'details': [
                {
                    'name': cls.get_attribute('name', 'unknown'),
                    'base_classes': cls.get_attribute('base_classes', []),
                    'line': cls.source_range.start.line if cls.source_range else None
                }
                for cls in classes
            ]
        }
    
    if analysis_type in ['all', 'imports']:
        # Analyse des imports
        imports = ust.get_nodes_by_type(NodeType.IMPORT_DECLARATION)
        analysis['imports'] = {
            'count': len(imports),
            'details': [
                {
                    'module': imp.get_attribute('module'),
                    'names': imp.get_attribute('names', []),
                    'type': imp.get_attribute('type', 'import'),
                    'line': imp.source_range.start.line if imp.source_range else None
                }
                for imp in imports
            ]
        }
    
    if analysis_type in ['all', 'complexity']:
        # Analyse de complexité basique
        all_nodes = []
        def count_nodes(node):
            all_nodes.append(node)
            for child in node.children:
                count_nodes(child)
        
        count_nodes(ust.root)
        
        # Compte les différents types de nœuds
        node_counts = {}
        for node in all_nodes:
            node_type = node.type.value
            node_counts[node_type] = node_counts.get(node_type, 0) + 1
        
        analysis['complexity'] = {
            'total_nodes': len(all_nodes),
            'node_types': node_counts,
            'depth': _calculate_ast_depth(ust.root),
            'cyclomatic_complexity': _estimate_cyclomatic_complexity(all_nodes)
        }
    
    return analysis


def _calculate_ast_depth(node, current_depth=0):
    """Calcule la profondeur maximale de l'AST"""
    if not node.children:
        return current_depth
    
    max_child_depth = 0
    for child in node.children:
        child_depth = _calculate_ast_depth(child, current_depth + 1)
        max_child_depth = max(max_child_depth, child_depth)
    
    return max_child_depth


def _estimate_cyclomatic_complexity(nodes):
    """Estime la complexité cyclomatique basée sur les nœuds de contrôle"""
    from src.models.ast_universal import NodeType
    
    complexity = 1  # Base complexity
    
    control_flow_nodes = [
        NodeType.IF_STATEMENT,
        NodeType.WHILE_STATEMENT,
        NodeType.FOR_STATEMENT,
        NodeType.BINARY_EXPRESSION  # Pour les conditions AND/OR
    ]
    
    for node in nodes:
        if node.type in control_flow_nodes:
            complexity += 1
    
    return complexity

