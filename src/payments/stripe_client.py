"""
Client Stripe pour la gestion des paiements de Léa
Gère les abonnements, paiements uniques et facturation
"""

import stripe
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from decimal import Decimal

logger = logging.getLogger(__name__)

class StripeClient:
    def __init__(self, secret_key: str, public_key: str):
        """
        Initialise le client Stripe
        
        Args:
            secret_key: Clé secrète Stripe
            public_key: Clé publique Stripe
        """
        stripe.api_key = secret_key
        self.public_key = public_key
        
        # Plans d'abonnement Léa
        self.subscription_plans = {
            "starter": {
                "name": "Léa Starter",
                "price": 29.99,
                "currency": "eur",
                "interval": "month",
                "features": [
                    "Analyse de code basique",
                    "Génération de code simple",
                    "5 projets maximum",
                    "Support email"
                ],
                "ai_credits": 1000,
                "max_projects": 5
            },
            "professional": {
                "name": "Léa Professional", 
                "price": 79.99,
                "currency": "eur",
                "interval": "month",
                "features": [
                    "Analyse de code avancée",
                    "Génération de code complexe",
                    "Projets illimités",
                    "Auto-pentest complet",
                    "Support prioritaire",
                    "Intégrations CI/CD"
                ],
                "ai_credits": 5000,
                "max_projects": -1  # Illimité
            },
            "enterprise": {
                "name": "Léa Enterprise",
                "price": 199.99,
                "currency": "eur", 
                "interval": "month",
                "features": [
                    "Toutes les fonctionnalités Pro",
                    "IA hybride complète",
                    "Architecture système",
                    "Support 24/7",
                    "Déploiement on-premise",
                    "Formation équipe",
                    "SLA garanti"
                ],
                "ai_credits": 20000,
                "max_projects": -1,
                "custom_features": True
            }
        }
    
    def create_customer(self, email: str, name: str, 
                       metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Crée un nouveau client Stripe
        
        Args:
            email: Email du client
            name: Nom du client
            metadata: Métadonnées additionnelles
            
        Returns:
            Informations du client créé
        """
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                metadata=metadata or {}
            )
            
            return {
                "success": True,
                "customer_id": customer.id,
                "email": customer.email,
                "name": customer.name,
                "created": datetime.fromtimestamp(customer.created).isoformat()
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Erreur création client Stripe: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    def create_subscription(self, customer_id: str, plan_id: str,
                          trial_days: int = 14) -> Dict[str, Any]:
        """
        Crée un abonnement pour un client
        
        Args:
            customer_id: ID du client Stripe
            plan_id: ID du plan (starter, professional, enterprise)
            trial_days: Jours d'essai gratuit
            
        Returns:
            Informations de l'abonnement
        """
        try:
            plan = self.subscription_plans.get(plan_id)
            if not plan:
                return {
                    "success": False,
                    "error": f"Plan {plan_id} non trouvé"
                }
            
            # Créer le prix si nécessaire
            price = stripe.Price.create(
                unit_amount=int(plan["price"] * 100),  # Centimes
                currency=plan["currency"],
                recurring={"interval": plan["interval"]},
                product_data={
                    "name": plan["name"],
                    "description": f"Abonnement {plan['name']} - {', '.join(plan['features'][:3])}"
                }
            )
            
            # Créer l'abonnement
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{"price": price.id}],
                trial_period_days=trial_days,
                metadata={
                    "plan_id": plan_id,
                    "ai_credits": plan["ai_credits"],
                    "max_projects": plan["max_projects"]
                }
            )
            
            return {
                "success": True,
                "subscription_id": subscription.id,
                "status": subscription.status,
                "current_period_start": datetime.fromtimestamp(
                    subscription.current_period_start
                ).isoformat(),
                "current_period_end": datetime.fromtimestamp(
                    subscription.current_period_end
                ).isoformat(),
                "trial_end": datetime.fromtimestamp(
                    subscription.trial_end
                ).isoformat() if subscription.trial_end else None,
                "plan": plan,
                "amount": plan["price"]
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Erreur création abonnement: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    def create_payment_intent(self, amount: float, currency: str = "eur",
                            customer_id: Optional[str] = None,
                            description: str = "") -> Dict[str, Any]:
        """
        Crée une intention de paiement pour un paiement unique
        
        Args:
            amount: Montant en euros
            currency: Devise
            customer_id: ID du client (optionnel)
            description: Description du paiement
            
        Returns:
            Intention de paiement
        """
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Centimes
                currency=currency,
                customer=customer_id,
                description=description,
                metadata={
                    "service": "lea_coding_assistant",
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            return {
                "success": True,
                "payment_intent_id": intent.id,
                "client_secret": intent.client_secret,
                "amount": amount,
                "currency": currency,
                "status": intent.status
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Erreur création payment intent: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    def get_subscription_status(self, subscription_id: str) -> Dict[str, Any]:
        """
        Récupère le statut d'un abonnement
        
        Args:
            subscription_id: ID de l'abonnement
            
        Returns:
            Statut de l'abonnement
        """
        try:
            subscription = stripe.Subscription.retrieve(subscription_id)
            
            return {
                "success": True,
                "subscription_id": subscription.id,
                "status": subscription.status,
                "current_period_start": datetime.fromtimestamp(
                    subscription.current_period_start
                ).isoformat(),
                "current_period_end": datetime.fromtimestamp(
                    subscription.current_period_end
                ).isoformat(),
                "cancel_at_period_end": subscription.cancel_at_period_end,
                "metadata": subscription.metadata
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Erreur récupération abonnement: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    def cancel_subscription(self, subscription_id: str, 
                          at_period_end: bool = True) -> Dict[str, Any]:
        """
        Annule un abonnement
        
        Args:
            subscription_id: ID de l'abonnement
            at_period_end: Annuler à la fin de la période
            
        Returns:
            Résultat de l'annulation
        """
        try:
            if at_period_end:
                subscription = stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=True
                )
            else:
                subscription = stripe.Subscription.delete(subscription_id)
            
            return {
                "success": True,
                "subscription_id": subscription.id,
                "status": subscription.status,
                "canceled_at": datetime.fromtimestamp(
                    subscription.canceled_at
                ).isoformat() if subscription.canceled_at else None
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Erreur annulation abonnement: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    def upgrade_subscription(self, subscription_id: str, 
                           new_plan_id: str) -> Dict[str, Any]:
        """
        Met à niveau un abonnement
        
        Args:
            subscription_id: ID de l'abonnement
            new_plan_id: Nouveau plan
            
        Returns:
            Résultat de la mise à niveau
        """
        try:
            new_plan = self.subscription_plans.get(new_plan_id)
            if not new_plan:
                return {
                    "success": False,
                    "error": f"Plan {new_plan_id} non trouvé"
                }
            
            # Récupérer l'abonnement actuel
            subscription = stripe.Subscription.retrieve(subscription_id)
            
            # Créer le nouveau prix
            new_price = stripe.Price.create(
                unit_amount=int(new_plan["price"] * 100),
                currency=new_plan["currency"],
                recurring={"interval": new_plan["interval"]},
                product_data={
                    "name": new_plan["name"]
                }
            )
            
            # Mettre à jour l'abonnement
            updated_subscription = stripe.Subscription.modify(
                subscription_id,
                items=[{
                    "id": subscription["items"]["data"][0].id,
                    "price": new_price.id
                }],
                metadata={
                    "plan_id": new_plan_id,
                    "ai_credits": new_plan["ai_credits"],
                    "max_projects": new_plan["max_projects"]
                },
                proration_behavior="always_invoice"
            )
            
            return {
                "success": True,
                "subscription_id": updated_subscription.id,
                "new_plan": new_plan,
                "status": updated_subscription.status,
                "upgraded_at": datetime.now().isoformat()
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Erreur upgrade abonnement: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    def get_customer_invoices(self, customer_id: str, 
                            limit: int = 10) -> Dict[str, Any]:
        """
        Récupère les factures d'un client
        
        Args:
            customer_id: ID du client
            limit: Nombre de factures à récupérer
            
        Returns:
            Liste des factures
        """
        try:
            invoices = stripe.Invoice.list(
                customer=customer_id,
                limit=limit
            )
            
            invoice_list = []
            for invoice in invoices.data:
                invoice_list.append({
                    "id": invoice.id,
                    "amount_paid": invoice.amount_paid / 100,
                    "currency": invoice.currency,
                    "status": invoice.status,
                    "created": datetime.fromtimestamp(invoice.created).isoformat(),
                    "invoice_pdf": invoice.invoice_pdf,
                    "hosted_invoice_url": invoice.hosted_invoice_url
                })
            
            return {
                "success": True,
                "invoices": invoice_list,
                "total_count": len(invoice_list)
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Erreur récupération factures: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    def create_usage_record(self, subscription_item_id: str, 
                          quantity: int, timestamp: Optional[int] = None) -> Dict[str, Any]:
        """
        Enregistre l'utilisation pour la facturation basée sur l'usage
        
        Args:
            subscription_item_id: ID de l'élément d'abonnement
            quantity: Quantité utilisée (ex: crédits IA)
            timestamp: Timestamp de l'utilisation
            
        Returns:
            Enregistrement d'utilisation
        """
        try:
            usage_record = stripe.SubscriptionItem.create_usage_record(
                subscription_item_id,
                quantity=quantity,
                timestamp=timestamp or int(datetime.now().timestamp())
            )
            
            return {
                "success": True,
                "usage_record_id": usage_record.id,
                "quantity": usage_record.quantity,
                "timestamp": datetime.fromtimestamp(usage_record.timestamp).isoformat()
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Erreur enregistrement usage: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    def get_available_plans(self) -> Dict[str, Any]:
        """
        Retourne les plans d'abonnement disponibles
        
        Returns:
            Liste des plans
        """
        return {
            "success": True,
            "plans": self.subscription_plans,
            "currency": "EUR",
            "trial_days": 14,
            "features_comparison": {
                "starter": "Idéal pour les développeurs individuels",
                "professional": "Parfait pour les équipes et projets complexes", 
                "enterprise": "Solution complète pour les grandes organisations"
            }
        }
    
    def validate_webhook(self, payload: str, signature: str, 
                        webhook_secret: str) -> Dict[str, Any]:
        """
        Valide un webhook Stripe
        
        Args:
            payload: Contenu du webhook
            signature: Signature Stripe
            webhook_secret: Secret du webhook
            
        Returns:
            Événement validé
        """
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, webhook_secret
            )
            
            return {
                "success": True,
                "event": event,
                "type": event["type"],
                "data": event["data"]
            }
            
        except ValueError as e:
            logger.error(f"Payload webhook invalide: {e}")
            return {
                "success": False,
                "error": "Payload invalide"
            }
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Signature webhook invalide: {e}")
            return {
                "success": False,
                "error": "Signature invalide"
            }
    
    def get_payment_stats(self) -> Dict[str, Any]:
        """
        Retourne les statistiques de paiement
        
        Returns:
            Statistiques Stripe
        """
        return {
            "provider": "Stripe",
            "supported_currencies": ["EUR", "USD", "GBP"],
            "payment_methods": [
                "card", "sepa_debit", "ideal", "bancontact", 
                "giropay", "sofort", "eps", "p24"
            ],
            "subscription_features": [
                "recurring_billing",
                "usage_based_billing", 
                "trial_periods",
                "proration",
                "dunning_management"
            ],
            "security": [
                "PCI_DSS_Level_1",
                "3D_Secure",
                "fraud_detection",
                "encryption"
            ],
            "public_key": self.public_key
        }

