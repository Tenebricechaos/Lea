"""
Système Zero Trust pour Léa
Implémente une architecture de sécurité Zero Trust où chaque requête est authentifiée,
autorisée et vérifiée, quel que soit son origine.
"""

import hashlib
import hmac
import time
import jwt
import secrets
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps
from flask import request, jsonify, current_app
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TrustLevel(Enum):
    """Niveaux de confiance dans l'architecture Zero Trust"""
    UNTRUSTED = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class ResourceType(Enum):
    """Types de ressources protégées"""
    CODE_PARSING = "code_parsing"
    CODE_GENERATION = "code_generation"
    CODE_ANALYSIS = "code_analysis"
    USER_DATA = "user_data"
    SYSTEM_CONFIG = "system_config"
    DEPLOYMENT = "deployment"
    MARKETPLACE = "marketplace"


@dataclass
class SecurityContext:
    """Contexte de sécurité pour une requête"""
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    trust_level: TrustLevel = TrustLevel.UNTRUSTED
    permissions: List[str] = field(default_factory=list)
    risk_score: float = 0.0
    timestamp: float = field(default_factory=time.time)
    
    def is_authorized(self, resource: ResourceType, action: str) -> bool:
        """Vérifie si le contexte est autorisé pour une ressource et action"""
        required_permission = f"{resource.value}:{action}"
        return required_permission in self.permissions or "admin:*" in self.permissions


@dataclass
class SecurityPolicy:
    """Politique de sécurité pour une ressource"""
    resource_type: ResourceType
    min_trust_level: TrustLevel
    required_permissions: List[str]
    max_risk_score: float = 0.7
    rate_limit: Optional[int] = None  # Requêtes par minute
    require_mfa: bool = False


class ZeroTrustEngine:
    """Moteur principal du système Zero Trust"""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.policies: Dict[str, SecurityPolicy] = {}
        self.active_sessions: Dict[str, SecurityContext] = {}
        self.rate_limits: Dict[str, List[float]] = {}
        self.blocked_ips: set = set()
        
        # Initialisation des politiques par défaut
        self._init_default_policies()
    
    def _init_default_policies(self):
        """Initialise les politiques de sécurité par défaut"""
        
        # Politique pour le parsing de code
        self.policies["parse_code"] = SecurityPolicy(
            resource_type=ResourceType.CODE_PARSING,
            min_trust_level=TrustLevel.LOW,
            required_permissions=["code:parse"],
            max_risk_score=0.5,
            rate_limit=100  # 100 requêtes par minute
        )
        
        # Politique pour la génération de code
        self.policies["generate_code"] = SecurityPolicy(
            resource_type=ResourceType.CODE_GENERATION,
            min_trust_level=TrustLevel.MEDIUM,
            required_permissions=["code:generate"],
            max_risk_score=0.3,
            rate_limit=20
        )
        
        # Politique pour l'analyse de code
        self.policies["analyze_code"] = SecurityPolicy(
            resource_type=ResourceType.CODE_ANALYSIS,
            min_trust_level=TrustLevel.LOW,
            required_permissions=["code:analyze"],
            max_risk_score=0.6,
            rate_limit=50
        )
        
        # Politique pour le déploiement
        self.policies["deploy"] = SecurityPolicy(
            resource_type=ResourceType.DEPLOYMENT,
            min_trust_level=TrustLevel.HIGH,
            required_permissions=["deploy:execute"],
            max_risk_score=0.1,
            rate_limit=5,
            require_mfa=True
        )
        
        # Politique pour la configuration système
        self.policies["system_config"] = SecurityPolicy(
            resource_type=ResourceType.SYSTEM_CONFIG,
            min_trust_level=TrustLevel.CRITICAL,
            required_permissions=["admin:config"],
            max_risk_score=0.0,
            rate_limit=10,
            require_mfa=True
        )
    
    def create_session(self, user_id: str, ip_address: str, user_agent: str) -> str:
        """Crée une nouvelle session sécurisée"""
        session_id = secrets.token_urlsafe(32)
        
        # Calcul du niveau de confiance initial
        trust_level = self._calculate_initial_trust(ip_address, user_agent)
        
        # Calcul du score de risque initial
        risk_score = self._calculate_risk_score(ip_address, user_agent)
        
        # Permissions par défaut (à adapter selon le rôle utilisateur)
        default_permissions = ["code:parse", "code:analyze"]
        
        context = SecurityContext(
            user_id=user_id,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent,
            trust_level=trust_level,
            permissions=default_permissions,
            risk_score=risk_score
        )
        
        self.active_sessions[session_id] = context
        
        logger.info(f"Session créée pour utilisateur {user_id}, trust_level: {trust_level.name}, risk_score: {risk_score}")
        
        return session_id
    
    def validate_request(self, session_id: str, policy_name: str, 
                        ip_address: str, user_agent: str) -> Tuple[bool, Optional[str]]:
        """Valide une requête selon les principes Zero Trust"""
        
        # Vérification de l'IP bloquée
        if ip_address in self.blocked_ips:
            logger.warning(f"Requête bloquée depuis IP {ip_address}")
            return False, "IP address blocked"
        
        # Vérification de la session
        if session_id not in self.active_sessions:
            logger.warning(f"Session invalide: {session_id}")
            return False, "Invalid session"
        
        context = self.active_sessions[session_id]
        
        # Vérification de la politique
        if policy_name not in self.policies:
            logger.error(f"Politique inconnue: {policy_name}")
            return False, "Unknown policy"
        
        policy = self.policies[policy_name]
        
        # Vérification du niveau de confiance
        if context.trust_level.value < policy.min_trust_level.value:
            logger.warning(f"Niveau de confiance insuffisant: {context.trust_level.name} < {policy.min_trust_level.name}")
            return False, "Insufficient trust level"
        
        # Vérification des permissions
        if not any(perm in context.permissions for perm in policy.required_permissions):
            logger.warning(f"Permissions insuffisantes pour {policy_name}")
            return False, "Insufficient permissions"
        
        # Vérification du score de risque
        if context.risk_score > policy.max_risk_score:
            logger.warning(f"Score de risque trop élevé: {context.risk_score} > {policy.max_risk_score}")
            return False, "Risk score too high"
        
        # Vérification du rate limiting
        if policy.rate_limit and not self._check_rate_limit(session_id, policy.rate_limit):
            logger.warning(f"Rate limit dépassé pour {session_id}")
            return False, "Rate limit exceeded"
        
        # Mise à jour du contexte de sécurité
        self._update_security_context(context, ip_address, user_agent)
        
        logger.info(f"Requête autorisée pour {session_id} sur {policy_name}")
        return True, None
    
    def _calculate_initial_trust(self, ip_address: str, user_agent: str) -> TrustLevel:
        """Calcule le niveau de confiance initial"""
        trust_score = 0
        
        # Vérification de l'IP (simulation)
        if self._is_known_good_ip(ip_address):
            trust_score += 2
        elif self._is_suspicious_ip(ip_address):
            trust_score -= 1
        
        # Vérification du User-Agent
        if self._is_legitimate_user_agent(user_agent):
            trust_score += 1
        
        # Conversion en niveau de confiance
        if trust_score >= 3:
            return TrustLevel.HIGH
        elif trust_score >= 1:
            return TrustLevel.MEDIUM
        elif trust_score >= 0:
            return TrustLevel.LOW
        else:
            return TrustLevel.UNTRUSTED
    
    def _calculate_risk_score(self, ip_address: str, user_agent: str) -> float:
        """Calcule le score de risque (0.0 = faible risque, 1.0 = risque élevé)"""
        risk_factors = []
        
        # Facteurs de risque IP
        if self._is_suspicious_ip(ip_address):
            risk_factors.append(0.3)
        
        if self._is_tor_ip(ip_address):
            risk_factors.append(0.4)
        
        # Facteurs de risque User-Agent
        if not self._is_legitimate_user_agent(user_agent):
            risk_factors.append(0.2)
        
        # Calcul du score final
        return min(sum(risk_factors), 1.0)
    
    def _check_rate_limit(self, session_id: str, limit: int) -> bool:
        """Vérifie le rate limiting"""
        now = time.time()
        minute_ago = now - 60
        
        if session_id not in self.rate_limits:
            self.rate_limits[session_id] = []
        
        # Nettoie les anciennes requêtes
        self.rate_limits[session_id] = [
            timestamp for timestamp in self.rate_limits[session_id]
            if timestamp > minute_ago
        ]
        
        # Vérifie la limite
        if len(self.rate_limits[session_id]) >= limit:
            return False
        
        # Ajoute la requête actuelle
        self.rate_limits[session_id].append(now)
        return True
    
    def _update_security_context(self, context: SecurityContext, 
                                ip_address: str, user_agent: str):
        """Met à jour le contexte de sécurité basé sur le comportement"""
        
        # Vérification de cohérence IP/User-Agent
        if context.ip_address != ip_address:
            context.risk_score += 0.1
            logger.warning(f"Changement d'IP détecté pour session {context.session_id}")
        
        if context.user_agent != user_agent:
            context.risk_score += 0.05
            logger.warning(f"Changement d'User-Agent détecté pour session {context.session_id}")
        
        # Mise à jour du timestamp
        context.timestamp = time.time()
        
        # Ajustement du niveau de confiance basé sur le comportement
        if context.risk_score > 0.8:
            context.trust_level = TrustLevel.UNTRUSTED
        elif context.risk_score > 0.5:
            context.trust_level = TrustLevel.LOW
    
    def _is_known_good_ip(self, ip_address: str) -> bool:
        """Vérifie si l'IP est connue comme fiable (simulation)"""
        # Dans un vrai système, ceci consulterait une base de données
        return ip_address.startswith("192.168.") or ip_address == "127.0.0.1"
    
    def _is_suspicious_ip(self, ip_address: str) -> bool:
        """Vérifie si l'IP est suspecte (simulation)"""
        # Dans un vrai système, ceci consulterait des listes de réputation
        suspicious_ranges = ["10.0.0.", "172.16."]
        return any(ip_address.startswith(range_) for range_ in suspicious_ranges)
    
    def _is_tor_ip(self, ip_address: str) -> bool:
        """Vérifie si l'IP est un nœud Tor (simulation)"""
        # Dans un vrai système, ceci consulterait la liste des nœuds Tor
        return False
    
    def _is_legitimate_user_agent(self, user_agent: str) -> bool:
        """Vérifie si le User-Agent semble légitime"""
        if not user_agent:
            return False
        
        legitimate_patterns = [
            "Mozilla", "Chrome", "Safari", "Firefox", "Edge",
            "curl", "Postman", "Python-requests"
        ]
        
        return any(pattern in user_agent for pattern in legitimate_patterns)
    
    def generate_jwt_token(self, context: SecurityContext) -> str:
        """Génère un token JWT pour le contexte de sécurité"""
        payload = {
            "user_id": context.user_id,
            "session_id": context.session_id,
            "trust_level": context.trust_level.value,
            "permissions": context.permissions,
            "risk_score": context.risk_score,
            "iat": int(time.time()),
            "exp": int(time.time()) + 3600  # Expire dans 1 heure
        }
        
        return jwt.encode(payload, self.secret_key, algorithm="HS256")
    
    def verify_jwt_token(self, token: str) -> Optional[SecurityContext]:
        """Vérifie et décode un token JWT"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            
            context = SecurityContext(
                user_id=payload["user_id"],
                session_id=payload["session_id"],
                trust_level=TrustLevel(payload["trust_level"]),
                permissions=payload["permissions"],
                risk_score=payload["risk_score"],
                timestamp=payload["iat"]
            )
            
            return context
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token JWT expiré")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Token JWT invalide")
            return None
    
    def block_ip(self, ip_address: str, reason: str):
        """Bloque une adresse IP"""
        self.blocked_ips.add(ip_address)
        logger.warning(f"IP {ip_address} bloquée: {reason}")
    
    def unblock_ip(self, ip_address: str):
        """Débloque une adresse IP"""
        self.blocked_ips.discard(ip_address)
        logger.info(f"IP {ip_address} débloquée")


# Instance globale du moteur Zero Trust
zero_trust_engine = ZeroTrustEngine(secrets.token_urlsafe(32))


def require_zero_trust(policy_name: str):
    """Décorateur pour protéger les endpoints avec Zero Trust"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Extraction des informations de la requête
            session_id = request.headers.get('X-Session-ID')
            ip_address = request.remote_addr
            user_agent = request.headers.get('User-Agent', '')
            
            if not session_id:
                return jsonify({
                    'error': 'Session ID required',
                    'code': 'MISSING_SESSION'
                }), 401
            
            # Validation Zero Trust
            is_valid, error_message = zero_trust_engine.validate_request(
                session_id, policy_name, ip_address, user_agent
            )
            
            if not is_valid:
                return jsonify({
                    'error': error_message,
                    'code': 'ZERO_TRUST_VIOLATION'
                }), 403
            
            # Ajout du contexte de sécurité à la requête
            request.security_context = zero_trust_engine.active_sessions[session_id]
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

