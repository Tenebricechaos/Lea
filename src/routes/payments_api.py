"""
API pour la gestion des paiements de Léa
Gère les abonnements, paiements et facturation via Stripe
"""

from flask import Blueprint, request, jsonify
import logging
from typing import Dict, Any

from ..payments.stripe_client import StripeClient

logger = logging.getLogger(__name__)

# Configuration des clés Stripe (à déplacer vers les variables d'environnement en production)
STRIPE_SECRET_KEY = "sk_test_51RDE1ZFth3yeGd9K3GcZovw4My4LeBd4WhlkgvtFCPfvQdDApog2604uH2XJkVUIaFt9XiKtn8To9007TvXeqjH300D82Fvb85"
STRIPE_PUBLIC_KEY = "pk_test_51RDE1ZFth3yeGd9K1och2XKZk00BnCDMWxTGespzMh2G62qBwBn0NUV5pTEtOkazi1OcvcTyhqd5BPwRmqiylcjQ00nfA19bfQ"

# Initialiser le client Stripe
stripe_client = StripeClient(STRIPE_SECRET_KEY, STRIPE_PUBLIC_KEY)

payments_api = Blueprint('payments_api', __name__)

@payments_api.route('/health', methods=['GET'])
def health_check():
    """Vérification de l'état de l'API paiements"""
    return jsonify({
        "status": "healthy",
        "service": "Léa Payments API",
        "version": "1.0.0",
        "provider": "Stripe",
        "capabilities": [
            "subscription_management",
            "one_time_payments",
            "invoice_generation",
            "usage_tracking",
            "webhook_handling"
        ]
    })

@payments_api.route('/plans', methods=['GET'])
def get_plans():
    """Récupère les plans d'abonnement disponibles"""
    try:
        plans = stripe_client.get_available_plans()
        return jsonify(plans)
        
    except Exception as e:
        logger.error(f"Erreur récupération plans: {e}")
        return jsonify({
            "success": False,
            "error": "Erreur interne du serveur"
        }), 500

@payments_api.route('/customer', methods=['POST'])
def create_customer():
    """
    Crée un nouveau client
    
    Body:
    {
        "email": "user@example.com",
        "name": "John Doe",
        "metadata": {}
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'email' not in data:
            return jsonify({
                "success": False,
                "error": "Le champ 'email' est requis"
            }), 400
        
        email = data['email']
        name = data.get('name', '')
        metadata = data.get('metadata', {})
        
        # Validation email basique
        if '@' not in email or '.' not in email:
            return jsonify({
                "success": False,
                "error": "Format d'email invalide"
            }), 400
        
        result = stripe_client.create_customer(email, name, metadata)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
        
    except Exception as e:
        logger.error(f"Erreur création client: {e}")
        return jsonify({
            "success": False,
            "error": "Erreur interne du serveur"
        }), 500

@payments_api.route('/subscription', methods=['POST'])
def create_subscription():
    """
    Crée un abonnement
    
    Body:
    {
        "customer_id": "cus_xxxxx",
        "plan_id": "professional",
        "trial_days": 14
    }
    """
    try:
        data = request.get_json()
        
        required_fields = ['customer_id', 'plan_id']
        for field in required_fields:
            if not data or field not in data:
                return jsonify({
                    "success": False,
                    "error": f"Le champ '{field}' est requis"
                }), 400
        
        customer_id = data['customer_id']
        plan_id = data['plan_id']
        trial_days = data.get('trial_days', 14)
        
        # Validation du plan
        valid_plans = ['starter', 'professional', 'enterprise']
        if plan_id not in valid_plans:
            return jsonify({
                "success": False,
                "error": f"Plan invalide. Plans disponibles: {valid_plans}"
            }), 400
        
        result = stripe_client.create_subscription(customer_id, plan_id, trial_days)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
        
    except Exception as e:
        logger.error(f"Erreur création abonnement: {e}")
        return jsonify({
            "success": False,
            "error": "Erreur interne du serveur"
        }), 500

@payments_api.route('/subscription/<subscription_id>', methods=['GET'])
def get_subscription_status(subscription_id):
    """Récupère le statut d'un abonnement"""
    try:
        result = stripe_client.get_subscription_status(subscription_id)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 404
        
    except Exception as e:
        logger.error(f"Erreur récupération abonnement: {e}")
        return jsonify({
            "success": False,
            "error": "Erreur interne du serveur"
        }), 500

@payments_api.route('/subscription/<subscription_id>/cancel', methods=['POST'])
def cancel_subscription(subscription_id):
    """
    Annule un abonnement
    
    Body:
    {
        "at_period_end": true
    }
    """
    try:
        data = request.get_json() or {}
        at_period_end = data.get('at_period_end', True)
        
        result = stripe_client.cancel_subscription(subscription_id, at_period_end)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
        
    except Exception as e:
        logger.error(f"Erreur annulation abonnement: {e}")
        return jsonify({
            "success": False,
            "error": "Erreur interne du serveur"
        }), 500

@payments_api.route('/subscription/<subscription_id>/upgrade', methods=['POST'])
def upgrade_subscription(subscription_id):
    """
    Met à niveau un abonnement
    
    Body:
    {
        "new_plan_id": "enterprise"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'new_plan_id' not in data:
            return jsonify({
                "success": False,
                "error": "Le champ 'new_plan_id' est requis"
            }), 400
        
        new_plan_id = data['new_plan_id']
        
        # Validation du plan
        valid_plans = ['starter', 'professional', 'enterprise']
        if new_plan_id not in valid_plans:
            return jsonify({
                "success": False,
                "error": f"Plan invalide. Plans disponibles: {valid_plans}"
            }), 400
        
        result = stripe_client.upgrade_subscription(subscription_id, new_plan_id)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
        
    except Exception as e:
        logger.error(f"Erreur upgrade abonnement: {e}")
        return jsonify({
            "success": False,
            "error": "Erreur interne du serveur"
        }), 500

@payments_api.route('/payment-intent', methods=['POST'])
def create_payment_intent():
    """
    Crée une intention de paiement pour un paiement unique
    
    Body:
    {
        "amount": 99.99,
        "currency": "eur",
        "customer_id": "cus_xxxxx",
        "description": "Crédits IA supplémentaires"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'amount' not in data:
            return jsonify({
                "success": False,
                "error": "Le champ 'amount' est requis"
            }), 400
        
        amount = data['amount']
        currency = data.get('currency', 'eur')
        customer_id = data.get('customer_id')
        description = data.get('description', 'Paiement Léa')
        
        # Validation du montant
        if not isinstance(amount, (int, float)) or amount <= 0:
            return jsonify({
                "success": False,
                "error": "Le montant doit être un nombre positif"
            }), 400
        
        # Validation de la devise
        valid_currencies = ['eur', 'usd', 'gbp']
        if currency not in valid_currencies:
            return jsonify({
                "success": False,
                "error": f"Devise invalide. Devises supportées: {valid_currencies}"
            }), 400
        
        result = stripe_client.create_payment_intent(amount, currency, customer_id, description)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
        
    except Exception as e:
        logger.error(f"Erreur création payment intent: {e}")
        return jsonify({
            "success": False,
            "error": "Erreur interne du serveur"
        }), 500

@payments_api.route('/customer/<customer_id>/invoices', methods=['GET'])
def get_customer_invoices(customer_id):
    """Récupère les factures d'un client"""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        if limit < 1 or limit > 100:
            return jsonify({
                "success": False,
                "error": "La limite doit être entre 1 et 100"
            }), 400
        
        result = stripe_client.get_customer_invoices(customer_id, limit)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 404
        
    except Exception as e:
        logger.error(f"Erreur récupération factures: {e}")
        return jsonify({
            "success": False,
            "error": "Erreur interne du serveur"
        }), 500

@payments_api.route('/usage-record', methods=['POST'])
def create_usage_record():
    """
    Enregistre l'utilisation pour la facturation basée sur l'usage
    
    Body:
    {
        "subscription_item_id": "si_xxxxx",
        "quantity": 100,
        "timestamp": 1234567890
    }
    """
    try:
        data = request.get_json()
        
        required_fields = ['subscription_item_id', 'quantity']
        for field in required_fields:
            if not data or field not in data:
                return jsonify({
                    "success": False,
                    "error": f"Le champ '{field}' est requis"
                }), 400
        
        subscription_item_id = data['subscription_item_id']
        quantity = data['quantity']
        timestamp = data.get('timestamp')
        
        # Validation de la quantité
        if not isinstance(quantity, int) or quantity <= 0:
            return jsonify({
                "success": False,
                "error": "La quantité doit être un entier positif"
            }), 400
        
        result = stripe_client.create_usage_record(subscription_item_id, quantity, timestamp)
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
        
    except Exception as e:
        logger.error(f"Erreur enregistrement usage: {e}")
        return jsonify({
            "success": False,
            "error": "Erreur interne du serveur"
        }), 500

@payments_api.route('/webhook', methods=['POST'])
def handle_webhook():
    """
    Gère les webhooks Stripe
    
    Headers:
    - Stripe-Signature: signature du webhook
    """
    try:
        payload = request.get_data(as_text=True)
        signature = request.headers.get('Stripe-Signature')
        
        if not signature:
            return jsonify({
                "success": False,
                "error": "Signature manquante"
            }), 400
        
        # Secret du webhook (à configurer dans Stripe Dashboard)
        webhook_secret = "whsec_test_webhook_secret"  # À remplacer par le vrai secret
        
        result = stripe_client.validate_webhook(payload, signature, webhook_secret)
        
        if not result['success']:
            return jsonify(result), 400
        
        event = result['event']
        event_type = event['type']
        
        # Traitement des différents types d'événements
        if event_type == 'customer.subscription.created':
            logger.info(f"Nouvel abonnement créé: {event['data']['object']['id']}")
            
        elif event_type == 'customer.subscription.updated':
            logger.info(f"Abonnement mis à jour: {event['data']['object']['id']}")
            
        elif event_type == 'customer.subscription.deleted':
            logger.info(f"Abonnement annulé: {event['data']['object']['id']}")
            
        elif event_type == 'invoice.payment_succeeded':
            logger.info(f"Paiement réussi: {event['data']['object']['id']}")
            
        elif event_type == 'invoice.payment_failed':
            logger.warning(f"Paiement échoué: {event['data']['object']['id']}")
            
        else:
            logger.info(f"Événement non traité: {event_type}")
        
        return jsonify({"success": True, "received": True})
        
    except Exception as e:
        logger.error(f"Erreur webhook: {e}")
        return jsonify({
            "success": False,
            "error": "Erreur interne du serveur"
        }), 500

@payments_api.route('/config', methods=['GET'])
def get_payment_config():
    """Configuration publique pour les paiements"""
    try:
        return jsonify({
            "success": True,
            "stripe_public_key": STRIPE_PUBLIC_KEY,
            "supported_currencies": ["EUR", "USD", "GBP"],
            "payment_methods": [
                "card", "sepa_debit", "ideal", "bancontact",
                "giropay", "sofort", "eps", "p24"
            ],
            "trial_period_days": 14,
            "plans": stripe_client.subscription_plans
        })
        
    except Exception as e:
        logger.error(f"Erreur config paiements: {e}")
        return jsonify({
            "success": False,
            "error": "Erreur interne du serveur"
        }), 500

@payments_api.route('/stats', methods=['GET'])
def get_payment_stats():
    """Statistiques du système de paiement"""
    try:
        stats = stripe_client.get_payment_stats()
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Erreur stats paiements: {e}")
        return jsonify({
            "success": False,
            "error": "Erreur interne du serveur"
        }), 500

# Endpoints pour les fonctionnalités avancées de Léa

@payments_api.route('/ai-credits/purchase', methods=['POST'])
def purchase_ai_credits():
    """
    Achat de crédits IA supplémentaires
    
    Body:
    {
        "customer_id": "cus_xxxxx",
        "credits": 1000,
        "payment_method": "card"
    }
    """
    try:
        data = request.get_json()
        
        required_fields = ['customer_id', 'credits']
        for field in required_fields:
            if not data or field not in data:
                return jsonify({
                    "success": False,
                    "error": f"Le champ '{field}' est requis"
                }), 400
        
        customer_id = data['customer_id']
        credits = data['credits']
        
        # Calcul du prix (0.01€ par crédit IA)
        price_per_credit = 0.01
        total_amount = credits * price_per_credit
        
        # Validation
        if credits < 100 or credits > 50000:
            return jsonify({
                "success": False,
                "error": "Le nombre de crédits doit être entre 100 et 50000"
            }), 400
        
        # Créer l'intention de paiement
        result = stripe_client.create_payment_intent(
            total_amount,
            "eur",
            customer_id,
            f"Achat de {credits} crédits IA pour Léa"
        )
        
        if result['success']:
            result['credits'] = credits
            result['price_per_credit'] = price_per_credit
            return jsonify(result), 201
        else:
            return jsonify(result), 400
        
    except Exception as e:
        logger.error(f"Erreur achat crédits IA: {e}")
        return jsonify({
            "success": False,
            "error": "Erreur interne du serveur"
        }), 500

@payments_api.route('/enterprise/quote', methods=['POST'])
def get_enterprise_quote():
    """
    Devis personnalisé pour les entreprises
    
    Body:
    {
        "company_name": "ACME Corp",
        "email": "contact@acme.com",
        "team_size": 50,
        "requirements": ["on_premise", "custom_training", "24_7_support"]
    }
    """
    try:
        data = request.get_json()
        
        required_fields = ['company_name', 'email', 'team_size']
        for field in required_fields:
            if not data or field not in data:
                return jsonify({
                    "success": False,
                    "error": f"Le champ '{field}' est requis"
                }), 400
        
        company_name = data['company_name']
        email = data['email']
        team_size = data['team_size']
        requirements = data.get('requirements', [])
        
        # Calcul du devis basé sur la taille de l'équipe et les exigences
        base_price = 199.99  # Prix Enterprise de base
        price_per_user = 15.0
        
        total_price = base_price + (team_size * price_per_user)
        
        # Ajustements selon les exigences
        requirement_costs = {
            "on_premise": 5000,
            "custom_training": 2500,
            "24_7_support": 1000,
            "dedicated_instance": 3000,
            "custom_integrations": 1500
        }
        
        additional_costs = sum(requirement_costs.get(req, 0) for req in requirements)
        total_price += additional_costs
        
        return jsonify({
            "success": True,
            "quote": {
                "company_name": company_name,
                "team_size": team_size,
                "base_price": base_price,
                "price_per_user": price_per_user,
                "user_cost": team_size * price_per_user,
                "additional_features": {req: requirement_costs.get(req, 0) for req in requirements},
                "additional_cost": additional_costs,
                "monthly_total": total_price,
                "annual_total": total_price * 12 * 0.9,  # 10% de réduction annuelle
                "currency": "EUR",
                "valid_until": "30 jours",
                "includes": [
                    "Toutes les fonctionnalités Enterprise",
                    "Support dédié",
                    "Formation équipe",
                    "Intégrations personnalisées",
                    "SLA garanti 99.9%"
                ] + requirements
            }
        })
        
    except Exception as e:
        logger.error(f"Erreur devis entreprise: {e}")
        return jsonify({
            "success": False,
            "error": "Erreur interne du serveur"
        }), 500

