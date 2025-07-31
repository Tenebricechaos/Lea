"""
Client DeepSeek pour la puissance de calcul avancée de Léa
Utilise l'API DeepSeek pour les tâches de raisonnement complexe et d'analyse approfondie
"""

import requests
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class DeepSeekClient:
    def __init__(self, api_key: str):
        """
        Initialise le client DeepSeek
        
        Args:
            api_key: Clé API DeepSeek
        """
        self.api_key = api_key
        self.base_url = "https://api.deepseek.com/v1"
        self.model = "deepseek-coder"  # Modèle spécialisé pour le code
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
    def _make_request(self, endpoint: str, data: Dict) -> Dict[str, Any]:
        """
        Effectue une requête à l'API DeepSeek
        
        Args:
            endpoint: Point de terminaison de l'API
            data: Données à envoyer
            
        Returns:
            Réponse de l'API
        """
        try:
            response = requests.post(
                f"{self.base_url}/{endpoint}",
                headers=self.headers,
                json=data,
                timeout=60
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur requête DeepSeek: {e}")
            raise
    
    def deep_code_analysis(self, code: str, language: str = "python") -> Dict[str, Any]:
        """
        Analyse approfondie de code avec raisonnement complexe
        
        Args:
            code: Code source à analyser
            language: Langage de programmation
            
        Returns:
            Dict contenant l'analyse approfondie
        """
        try:
            prompt = f"""Effectue une analyse approfondie et technique de ce code {language}.

Analyse requise:
1. **Architecture et Design Patterns**
   - Patterns utilisés ou recommandés
   - Qualité de l'architecture
   - Couplage et cohésion

2. **Complexité Algorithmique**
   - Complexité temporelle et spatiale
   - Optimisations possibles
   - Goulots d'étranglement

3. **Sécurité Avancée**
   - Vulnérabilités subtiles
   - Attaques potentielles
   - Mesures de protection

4. **Maintenabilité et Évolutivité**
   - Facilité de maintenance
   - Extensibilité
   - Refactoring nécessaire

5. **Performance et Scalabilité**
   - Points de performance critiques
   - Scalabilité horizontale/verticale
   - Optimisations système

Code à analyser:
```{language}
{code}
```

Fournis une analyse technique détaillée avec des recommandations concrètes."""

            data = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "Tu es un expert en analyse de code avec une expertise approfondie en architecture logicielle, sécurité, et optimisation. Fournis des analyses techniques détaillées et des recommandations précises."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                "temperature": 0.2,
                "max_tokens": 2500
            }
            
            response = self._make_request("chat/completions", data)
            
            analysis = response["choices"][0]["message"]["content"]
            
            return {
                "success": True,
                "deep_analysis": analysis,
                "language": language,
                "model": self.model,
                "timestamp": datetime.now().isoformat(),
                "tokens_used": response.get("usage", {}).get("total_tokens", 0)
            }
            
        except Exception as e:
            logger.error(f"Erreur analyse approfondie DeepSeek: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def complex_problem_solving(self, problem_description: str, 
                               context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Résolution de problèmes complexes avec raisonnement avancé
        
        Args:
            problem_description: Description du problème à résoudre
            context: Contexte additionnel
            
        Returns:
            Dict contenant la solution et le raisonnement
        """
        try:
            context_str = json.dumps(context) if context else "Aucun contexte spécifique"
            
            prompt = f"""Résous ce problème complexe en utilisant un raisonnement structuré et approfondi.

Problème: {problem_description}

Contexte: {context_str}

Méthode de résolution:
1. **Analyse du problème**
   - Décomposition en sous-problèmes
   - Identification des contraintes
   - Définition des objectifs

2. **Exploration des solutions**
   - Approches possibles
   - Avantages et inconvénients
   - Faisabilité technique

3. **Solution recommandée**
   - Solution détaillée étape par étape
   - Justification du choix
   - Plan d'implémentation

4. **Considérations avancées**
   - Gestion des cas limites
   - Optimisations possibles
   - Maintenance et évolution

Fournis une solution complète et bien raisonnée."""

            data = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "Tu es un expert en résolution de problèmes complexes avec une capacité de raisonnement avancée. Tu décomposes les problèmes méthodiquement et proposes des solutions optimales."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 2000
            }
            
            response = self._make_request("chat/completions", data)
            
            solution = response["choices"][0]["message"]["content"]
            
            return {
                "success": True,
                "solution": solution,
                "problem": problem_description,
                "model": self.model,
                "timestamp": datetime.now().isoformat(),
                "tokens_used": response.get("usage", {}).get("total_tokens", 0)
            }
            
        except Exception as e:
            logger.error(f"Erreur résolution problème DeepSeek: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def advanced_code_generation(self, requirements: str, language: str = "python",
                                architecture_style: str = "clean") -> Dict[str, Any]:
        """
        Génération de code avancée avec architecture sophistiquée
        
        Args:
            requirements: Spécifications détaillées
            language: Langage de programmation
            architecture_style: Style d'architecture (clean, hexagonal, microservices, etc.)
            
        Returns:
            Dict contenant le code généré et l'architecture
        """
        try:
            prompt = f"""Génère du code {language} professionnel selon ces spécifications.

Spécifications: {requirements}

Style d'architecture: {architecture_style}

Exigences de génération:
1. **Architecture**
   - Structure modulaire et extensible
   - Séparation des responsabilités
   - Patterns appropriés

2. **Qualité du code**
   - Code propre et lisible
   - Documentation intégrée
   - Tests unitaires inclus

3. **Sécurité**
   - Validation des entrées
   - Gestion des erreurs
   - Bonnes pratiques sécuritaires

4. **Performance**
   - Optimisations appropriées
   - Gestion efficace des ressources
   - Scalabilité

5. **Maintenabilité**
   - Code facilement modifiable
   - Configuration externalisée
   - Logging approprié

Génère un code complet, professionnel et prêt pour la production."""

            data = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": f"Tu es un architecte logiciel expert spécialisé en {language}. Tu génères du code de qualité production avec une architecture solide et des bonnes pratiques avancées."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.4,
                "max_tokens": 3000
            }
            
            response = self._make_request("chat/completions", data)
            
            generated_code = response["choices"][0]["message"]["content"]
            
            return {
                "success": True,
                "code": generated_code,
                "language": language,
                "architecture_style": architecture_style,
                "model": self.model,
                "timestamp": datetime.now().isoformat(),
                "tokens_used": response.get("usage", {}).get("total_tokens", 0)
            }
            
        except Exception as e:
            logger.error(f"Erreur génération code avancée DeepSeek: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def system_architecture_design(self, requirements: str, 
                                  scale: str = "medium") -> Dict[str, Any]:
        """
        Conception d'architecture système complète
        
        Args:
            requirements: Exigences du système
            scale: Échelle du système (small, medium, large, enterprise)
            
        Returns:
            Dict contenant la conception d'architecture
        """
        try:
            prompt = f"""Conçois une architecture système complète pour ces exigences.

Exigences: {requirements}

Échelle: {scale}

Conception requise:
1. **Architecture globale**
   - Diagramme d'architecture
   - Composants principaux
   - Flux de données

2. **Technologies recommandées**
   - Stack technique
   - Bases de données
   - Infrastructure

3. **Patterns et principes**
   - Patterns architecturaux
   - Principes de design
   - Bonnes pratiques

4. **Scalabilité et performance**
   - Stratégies de mise à l'échelle
   - Optimisations
   - Monitoring

5. **Sécurité et fiabilité**
   - Mesures de sécurité
   - Haute disponibilité
   - Récupération de désastre

6. **Plan d'implémentation**
   - Phases de développement
   - Priorités
   - Risques et mitigation

Fournis une conception d'architecture détaillée et professionnelle."""

            data = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "Tu es un architecte système senior avec une expertise en conception d'architectures scalables et robustes. Tu fournis des conceptions détaillées et pratiques."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 3500
            }
            
            response = self._make_request("chat/completions", data)
            
            architecture_design = response["choices"][0]["message"]["content"]
            
            return {
                "success": True,
                "architecture": architecture_design,
                "scale": scale,
                "model": self.model,
                "timestamp": datetime.now().isoformat(),
                "tokens_used": response.get("usage", {}).get("total_tokens", 0)
            }
            
        except Exception as e:
            logger.error(f"Erreur conception architecture DeepSeek: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def performance_optimization(self, code: str, language: str = "python",
                               target_metrics: List[str] = None) -> Dict[str, Any]:
        """
        Optimisation de performance avancée
        
        Args:
            code: Code à optimiser
            language: Langage de programmation
            target_metrics: Métriques cibles (latency, throughput, memory, cpu)
            
        Returns:
            Dict contenant les optimisations
        """
        try:
            if target_metrics is None:
                target_metrics = ["latency", "throughput", "memory"]
            
            metrics_str = ", ".join(target_metrics)
            
            prompt = f"""Optimise ce code {language} pour améliorer les performances.

Métriques cibles: {metrics_str}

Code à optimiser:
```{language}
{code}
```

Optimisations requises:
1. **Analyse de performance**
   - Profiling du code
   - Identification des goulots
   - Métriques actuelles

2. **Optimisations algorithmiques**
   - Amélioration de la complexité
   - Structures de données optimales
   - Algorithmes plus efficaces

3. **Optimisations système**
   - Gestion mémoire
   - I/O optimisées
   - Parallélisation

4. **Code optimisé**
   - Version améliorée
   - Changements détaillés
   - Gains attendus

5. **Benchmarking**
   - Tests de performance
   - Comparaisons avant/après
   - Métriques d'amélioration

Fournis des optimisations concrètes et mesurables."""

            data = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": f"Tu es un expert en optimisation de performance avec une connaissance approfondie des optimisations {language} et système. Tu fournis des améliorations concrètes et mesurables."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.2,
                "max_tokens": 2500
            }
            
            response = self._make_request("chat/completions", data)
            
            optimization = response["choices"][0]["message"]["content"]
            
            return {
                "success": True,
                "optimization": optimization,
                "language": language,
                "target_metrics": target_metrics,
                "model": self.model,
                "timestamp": datetime.now().isoformat(),
                "tokens_used": response.get("usage", {}).get("total_tokens", 0)
            }
            
        except Exception as e:
            logger.error(f"Erreur optimisation performance DeepSeek: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """
        Retourne les statistiques d'utilisation
        
        Returns:
            Dict contenant les stats d'usage
        """
        return {
            "model": self.model,
            "provider": "DeepSeek",
            "capabilities": [
                "deep_code_analysis",
                "complex_problem_solving",
                "advanced_code_generation",
                "system_architecture_design",
                "performance_optimization"
            ],
            "timestamp": datetime.now().isoformat()
        }

