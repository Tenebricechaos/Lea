#!/usr/bin/env python3
"""
Script de test pour le système de sécurité de Léa
Teste les fonctionnalités Zero Trust et d'auto-pentest.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.security.zero_trust import zero_trust_engine, TrustLevel
from src.security.auto_pentest import auto_pentest_engine, VulnerabilityType, SeverityLevel
from src.parsers.base_parser import parse_code, parser_registry
from src.parsers.python_parser import PythonParser
from src.parsers.javascript_parser import JavaScriptParser


def test_zero_trust_system():
    """Test du système Zero Trust"""
    print("=== Test du Système Zero Trust ===")
    
    # Enregistrement des parsers
    parser_registry.register_parser(PythonParser())
    parser_registry.register_parser(JavaScriptParser())
    
    try:
        # Test de création de session
        session_id = zero_trust_engine.create_session(
            user_id="test_user",
            ip_address="192.168.1.100",
            user_agent="Mozilla/5.0 (Test Browser)"
        )
        
        print(f"✓ Session créée: {session_id}")
        
        context = zero_trust_engine.active_sessions[session_id]
        print(f"  - Niveau de confiance: {context.trust_level.name}")
        print(f"  - Score de risque: {context.risk_score}")
        print(f"  - Permissions: {context.permissions}")
        
        # Test de validation de requête
        is_valid, error = zero_trust_engine.validate_request(
            session_id, "parse_code", "192.168.1.100", "Mozilla/5.0 (Test Browser)"
        )
        
        if is_valid:
            print("✓ Validation de requête réussie")
        else:
            print(f"✗ Validation échouée: {error}")
        
        # Test de génération JWT
        jwt_token = zero_trust_engine.generate_jwt_token(context)
        print(f"✓ Token JWT généré: {jwt_token[:50]}...")
        
        # Test de vérification JWT
        decoded_context = zero_trust_engine.verify_jwt_token(jwt_token)
        if decoded_context:
            print("✓ Vérification JWT réussie")
        else:
            print("✗ Vérification JWT échouée")
        
        # Test de blocage IP
        zero_trust_engine.block_ip("10.0.0.1", "Test de blocage")
        print("✓ IP bloquée avec succès")
        
        # Test de validation avec IP bloquée
        is_valid, error = zero_trust_engine.validate_request(
            session_id, "parse_code", "10.0.0.1", "Mozilla/5.0 (Test Browser)"
        )
        
        if not is_valid and "blocked" in error.lower():
            print("✓ Blocage IP fonctionne correctement")
        else:
            print("✗ Blocage IP ne fonctionne pas")
        
    except Exception as e:
        print(f"✗ Erreur: {e}")
        import traceback
        traceback.print_exc()


def test_auto_pentest_static():
    """Test du système d'auto-pentest - analyse statique"""
    print("\n=== Test de l'Auto-Pentest - Analyse Statique ===")
    
    # Code vulnérable pour les tests
    vulnerable_code = '''
import os
import subprocess

def unsafe_function(user_input):
    # Vulnérabilité: Command Injection
    os.system("ls " + user_input)
    
    # Vulnérabilité: SQL Injection
    query = "SELECT * FROM users WHERE name = '" + user_input + "'"
    
    # Vulnérabilité: Hardcoded Secret
    api_key = "sk-1234567890abcdef"
    password = "admin123"
    
    # Vulnérabilité: Unsafe Eval
    result = eval(user_input)
    
    return result

def weak_crypto():
    import hashlib
    # Vulnérabilité: Weak Cryptography
    hash_value = hashlib.md5(b"password").hexdigest()
    return hash_value
'''
    
    try:
        # Scan de sécurité
        report = auto_pentest_engine.scan_code(vulnerable_code, "test_vulnerable.py", "python")
        
        print(f"✓ Scan terminé: {report.scan_id}")
        print(f"  - Vulnérabilités trouvées: {len(report.vulnerabilities)}")
        print(f"  - Durée du scan: {report.end_time - report.start_time:.2f}s")
        
        # Analyse par sévérité
        severity_counts = report.get_severity_counts()
        for severity, count in severity_counts.items():
            if count > 0:
                print(f"  - {severity}: {count}")
        
        # Détails des vulnérabilités critiques et élevées
        high_vulns = [v for v in report.vulnerabilities if v.severity in [SeverityLevel.CRITICAL, SeverityLevel.HIGH]]
        print(f"\n  Vulnérabilités critiques/élevées:")
        for vuln in high_vulns:
            print(f"    * {vuln.title} (ligne {vuln.line_number})")
            print(f"      {vuln.description}")
            print(f"      CWE: {vuln.cwe_id}")
        
        # Plan de remédiation
        remediation_plan = auto_pentest_engine.generate_remediation_plan(report)
        print(f"\n  Plan de remédiation:")
        print(f"    - Effort total estimé: {remediation_plan['estimated_total_effort']} heures")
        print(f"    - Recommandations générales: {len(remediation_plan['recommendations'])}")
        
    except Exception as e:
        print(f"✗ Erreur: {e}")
        import traceback
        traceback.print_exc()


def test_auto_pentest_ast():
    """Test du système d'auto-pentest - analyse ASU"""
    print("\n=== Test de l'Auto-Pentest - Analyse ASU ===")
    
    # Code JavaScript vulnérable
    js_code = '''
function processData(userInput) {
    // Vulnérabilité détectable dans l'ASU
    eval(userInput);
    
    document.innerHTML = userInput;
    
    return userInput;
}

function dangerousCall() {
    system("rm -rf /");
}
'''
    
    try:
        # Parse en ASU
        ust = parse_code(js_code, "javascript")
        print(f"✓ Code parsé en ASU: {len(ust.root.children)} nœuds racine")
        
        # Scan de sécurité sur l'ASU
        report = auto_pentest_engine.scan_ast(ust)
        
        print(f"✓ Scan ASU terminé: {report.scan_id}")
        print(f"  - Vulnérabilités trouvées: {len(report.vulnerabilities)}")
        
        # Détails des vulnérabilités
        for vuln in report.vulnerabilities:
            print(f"    * {vuln.title}")
            print(f"      Type: {vuln.type.value}")
            print(f"      Sévérité: {vuln.severity.name}")
        
    except Exception as e:
        print(f"✗ Erreur: {e}")
        import traceback
        traceback.print_exc()


def test_security_integration():
    """Test d'intégration des systèmes de sécurité"""
    print("\n=== Test d'Intégration Sécurité ===")
    
    try:
        # Création d'une session avec permissions élevées
        session_id = zero_trust_engine.create_session(
            user_id="security_admin",
            ip_address="127.0.0.1",
            user_agent="Léa Security Scanner"
        )
        
        # Mise à jour des permissions pour les tests de sécurité
        context = zero_trust_engine.active_sessions[session_id]
        context.permissions.extend(["code:generate", "deploy:execute", "admin:config"])
        context.trust_level = TrustLevel.HIGH
        
        print(f"✓ Session admin créée: {session_id}")
        
        # Test de validation pour différentes politiques
        policies_to_test = ["parse_code", "generate_code", "analyze_code"]
        
        for policy in policies_to_test:
            is_valid, error = zero_trust_engine.validate_request(
                session_id, policy, "127.0.0.1", "Léa Security Scanner"
            )
            
            status = "✓" if is_valid else "✗"
            print(f"  {status} Politique {policy}: {'Autorisé' if is_valid else error}")
        
        # Test de scan avec contexte de sécurité
        test_code = "def secure_function(): return 'safe'"
        report = auto_pentest_engine.scan_code(test_code, "secure.py", "python")
        
        print(f"✓ Scan sécurisé effectué: {len(report.vulnerabilities)} vulnérabilités")
        
        # Test de rate limiting
        print("\n  Test de rate limiting:")
        for i in range(3):
            is_valid, error = zero_trust_engine.validate_request(
                session_id, "parse_code", "127.0.0.1", "Léa Security Scanner"
            )
            print(f"    Requête {i+1}: {'✓' if is_valid else '✗'}")
        
    except Exception as e:
        print(f"✗ Erreur: {e}")
        import traceback
        traceback.print_exc()


def test_vulnerability_detection():
    """Test de détection de vulnérabilités spécifiques"""
    print("\n=== Test de Détection de Vulnérabilités ===")
    
    test_cases = [
        {
            'name': 'SQL Injection',
            'code': 'query = "SELECT * FROM users WHERE id = " + user_id',
            'expected_type': VulnerabilityType.SQL_INJECTION
        },
        {
            'name': 'XSS',
            'code': 'document.innerHTML = userInput;',
            'expected_type': VulnerabilityType.XSS
        },
        {
            'name': 'Command Injection',
            'code': 'os.system("ls " + filename)',
            'expected_type': VulnerabilityType.COMMAND_INJECTION
        },
        {
            'name': 'Hardcoded Secret',
            'code': 'api_key = "sk-1234567890abcdef"',
            'expected_type': VulnerabilityType.HARDCODED_SECRETS
        },
        {
            'name': 'Unsafe Eval',
            'code': 'result = eval(user_input)',
            'expected_type': VulnerabilityType.UNSAFE_EVAL
        }
    ]
    
    for test_case in test_cases:
        try:
            report = auto_pentest_engine.scan_code(test_case['code'])
            
            # Vérification de la détection
            detected_types = [v.type for v in report.vulnerabilities]
            
            if test_case['expected_type'] in detected_types:
                print(f"✓ {test_case['name']}: Détecté correctement")
            else:
                print(f"✗ {test_case['name']}: Non détecté")
                print(f"  Types détectés: {[t.value for t in detected_types]}")
        
        except Exception as e:
            print(f"✗ {test_case['name']}: Erreur - {e}")


if __name__ == "__main__":
    print("🔒 Tests du Système de Sécurité de Léa")
    print("=" * 50)
    
    test_zero_trust_system()
    test_auto_pentest_static()
    test_auto_pentest_ast()
    test_security_integration()
    test_vulnerability_detection()
    
    print("\n" + "=" * 50)
    print("🔒 Tests de sécurité terminés!")

