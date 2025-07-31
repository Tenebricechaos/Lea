"""
API de sécurité pour Léa
Fournit les endpoints pour la gestion de la sécurité Zero Trust et l'auto-pentest.
"""

from flask import Blueprint, request, jsonify
from typing import Dict, Any, Optional
import traceback
import secrets

from src.security.zero_trust import zero_trust_engine, require_zero_trust, TrustLevel
from src.security.auto_pentest import auto_pentest_engine
from src.parsers.base_parser import parse_code

# Création du blueprint
security_bp = Blueprint('security', __name__)


@security_bp.route('/auth/login', methods=['POST'])
def login():
    """
    Authentification et création de session Zero Trust
    
    Body JSON:
    {
        "username": "nom d'utilisateur",
        "password": "mot de passe"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'username' not in data or 'password' not in data:
            return jsonify({
                'error': 'Username and password are required'
            }), 400
        
        username = data['username']
        password = data['password']
        
        # Simulation d'authentification (à remplacer par une vraie vérification)
        if username == "demo" and password == "demo123":
            # Création de session Zero Trust
            ip_address = request.remote_addr
            user_agent = request.headers.get('User-Agent', '')
            
            session_id = zero_trust_engine.create_session(username, ip_address, user_agent)
            context = zero_trust_engine.active_sessions[session_id]
            
            # Génération du token JWT
            jwt_token = zero_trust_engine.generate_jwt_token(context)
            
            return jsonify({
                'success': True,
                'session_id': session_id,
                'jwt_token': jwt_token,
                'trust_level': context.trust_level.name,
                'permissions': context.permissions,
                'risk_score': context.risk_score
            })
        else:
            return jsonify({
                'error': 'Invalid credentials'
            }), 401
            
    except Exception as e:
        return jsonify({
            'error': f'Authentication error: {str(e)}'
        }), 500


@security_bp.route('/auth/session', methods=['GET'])
def get_session_info():
    """Récupère les informations de session actuelle"""
    try:
        session_id = request.headers.get('X-Session-ID')
        
        if not session_id:
            return jsonify({
                'error': 'Session ID required'
            }), 401
        
        if session_id not in zero_trust_engine.active_sessions:
            return jsonify({
                'error': 'Invalid session'
            }), 401
        
        context = zero_trust_engine.active_sessions[session_id]
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'user_id': context.user_id,
            'trust_level': context.trust_level.name,
            'permissions': context.permissions,
            'risk_score': context.risk_score,
            'ip_address': context.ip_address,
            'session_age': context.timestamp
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Session error: {str(e)}'
        }), 500


@security_bp.route('/pentest/scan-code', methods=['POST'])
@require_zero_trust('analyze_code')
def scan_code_security():
    """
    Effectue un scan de sécurité sur du code source
    
    Body JSON:
    {
        "source_code": "code source à analyser",
        "language": "langage (optionnel)",
        "file_path": "chemin du fichier (optionnel)"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'source_code' not in data:
            return jsonify({
                'error': 'source_code field is required'
            }), 400
        
        source_code = data['source_code']
        language = data.get('language')
        file_path = data.get('file_path')
        
        # Scan de sécurité
        report = auto_pentest_engine.scan_code(source_code, file_path, language)
        
        # Génération du plan de remédiation
        remediation_plan = auto_pentest_engine.generate_remediation_plan(report)
        
        return jsonify({
            'success': True,
            'scan_report': report.to_dict(),
            'remediation_plan': remediation_plan
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Security scan error: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500


@security_bp.route('/pentest/scan-ast', methods=['POST'])
@require_zero_trust('analyze_code')
def scan_ast_security():
    """
    Effectue un scan de sécurité sur un ASU
    
    Body JSON:
    {
        "source_code": "code source",
        "language": "langage (optionnel)"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'source_code' not in data:
            return jsonify({
                'error': 'source_code field is required'
            }), 400
        
        source_code = data['source_code']
        language = data.get('language')
        
        # Parse le code en ASU
        ust = parse_code(source_code, language)
        
        # Scan de sécurité sur l'ASU
        report = auto_pentest_engine.scan_ast(ust)
        
        # Génération du plan de remédiation
        remediation_plan = auto_pentest_engine.generate_remediation_plan(report)
        
        return jsonify({
            'success': True,
            'scan_report': report.to_dict(),
            'remediation_plan': remediation_plan,
            'ast_metadata': ust.metadata
        })
        
    except Exception as e:
        return jsonify({
            'error': f'AST security scan error: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500


@security_bp.route('/pentest/scan-application', methods=['POST'])
@require_zero_trust('deploy')
def scan_application_security():
    """
    Effectue un scan de sécurité dynamique sur une application
    
    Body JSON:
    {
        "base_url": "URL de base de l'application",
        "endpoints": ["liste", "des", "endpoints"]
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'base_url' not in data:
            return jsonify({
                'error': 'base_url field is required'
            }), 400
        
        base_url = data['base_url']
        endpoints = data.get('endpoints', ['/'])
        
        # Scan de sécurité dynamique
        report = auto_pentest_engine.scan_application(base_url, endpoints)
        
        # Génération du plan de remédiation
        remediation_plan = auto_pentest_engine.generate_remediation_plan(report)
        
        return jsonify({
            'success': True,
            'scan_report': report.to_dict(),
            'remediation_plan': remediation_plan
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Application security scan error: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500


@security_bp.route('/pentest/reports/<scan_id>', methods=['GET'])
@require_zero_trust('analyze_code')
def get_scan_report(scan_id: str):
    """Récupère un rapport de scan spécifique"""
    try:
        report = auto_pentest_engine.get_scan_report(scan_id)
        
        if not report:
            return jsonify({
                'error': 'Scan report not found'
            }), 404
        
        return jsonify({
            'success': True,
            'scan_report': report.to_dict()
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Error retrieving scan report: {str(e)}'
        }), 500


@security_bp.route('/pentest/reports', methods=['GET'])
@require_zero_trust('analyze_code')
def list_scan_reports():
    """Liste tous les rapports de scan"""
    try:
        reports = []
        
        for scan_id, report in auto_pentest_engine.scan_history.items():
            reports.append({
                'scan_id': scan_id,
                'target': report.target,
                'start_time': report.start_time,
                'end_time': report.end_time,
                'vulnerability_count': len(report.vulnerabilities),
                'severity_counts': report.get_severity_counts(),
                'scan_type': report.scan_type
            })
        
        # Tri par date de création (plus récent en premier)
        reports.sort(key=lambda x: x['start_time'], reverse=True)
        
        return jsonify({
            'success': True,
            'reports': reports,
            'total_reports': len(reports),
            'active_scans': auto_pentest_engine.get_active_scans()
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Error listing scan reports: {str(e)}'
        }), 500


@security_bp.route('/zero-trust/policies', methods=['GET'])
@require_zero_trust('system_config')
def get_security_policies():
    """Récupère les politiques de sécurité Zero Trust"""
    try:
        policies = {}
        
        for policy_name, policy in zero_trust_engine.policies.items():
            policies[policy_name] = {
                'resource_type': policy.resource_type.value,
                'min_trust_level': policy.min_trust_level.name,
                'required_permissions': policy.required_permissions,
                'max_risk_score': policy.max_risk_score,
                'rate_limit': policy.rate_limit,
                'require_mfa': policy.require_mfa
            }
        
        return jsonify({
            'success': True,
            'policies': policies
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Error retrieving security policies: {str(e)}'
        }), 500


@security_bp.route('/zero-trust/sessions', methods=['GET'])
@require_zero_trust('system_config')
def list_active_sessions():
    """Liste les sessions actives"""
    try:
        sessions = []
        
        for session_id, context in zero_trust_engine.active_sessions.items():
            sessions.append({
                'session_id': session_id,
                'user_id': context.user_id,
                'ip_address': context.ip_address,
                'trust_level': context.trust_level.name,
                'risk_score': context.risk_score,
                'permissions': context.permissions,
                'created_at': context.timestamp
            })
        
        return jsonify({
            'success': True,
            'active_sessions': sessions,
            'total_sessions': len(sessions)
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Error listing active sessions: {str(e)}'
        }), 500


@security_bp.route('/zero-trust/block-ip', methods=['POST'])
@require_zero_trust('system_config')
def block_ip_address():
    """
    Bloque une adresse IP
    
    Body JSON:
    {
        "ip_address": "adresse IP à bloquer",
        "reason": "raison du blocage"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'ip_address' not in data:
            return jsonify({
                'error': 'ip_address field is required'
            }), 400
        
        ip_address = data['ip_address']
        reason = data.get('reason', 'Manual block')
        
        zero_trust_engine.block_ip(ip_address, reason)
        
        return jsonify({
            'success': True,
            'message': f'IP address {ip_address} has been blocked',
            'reason': reason
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Error blocking IP address: {str(e)}'
        }), 500


@security_bp.route('/zero-trust/unblock-ip', methods=['POST'])
@require_zero_trust('system_config')
def unblock_ip_address():
    """
    Débloque une adresse IP
    
    Body JSON:
    {
        "ip_address": "adresse IP à débloquer"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'ip_address' not in data:
            return jsonify({
                'error': 'ip_address field is required'
            }), 400
        
        ip_address = data['ip_address']
        
        zero_trust_engine.unblock_ip(ip_address)
        
        return jsonify({
            'success': True,
            'message': f'IP address {ip_address} has been unblocked'
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Error unblocking IP address: {str(e)}'
        }), 500


@security_bp.route('/health', methods=['GET'])
def security_health_check():
    """Vérification de l'état du système de sécurité"""
    try:
        return jsonify({
            'success': True,
            'service': 'Léa Security System',
            'version': '1.0.0',
            'status': 'healthy',
            'zero_trust': {
                'active_sessions': len(zero_trust_engine.active_sessions),
                'blocked_ips': len(zero_trust_engine.blocked_ips),
                'policies_loaded': len(zero_trust_engine.policies)
            },
            'auto_pentest': {
                'scan_history': len(auto_pentest_engine.scan_history),
                'active_scans': len(auto_pentest_engine.active_scans)
            }
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Health check error: {str(e)}'
        }), 500

