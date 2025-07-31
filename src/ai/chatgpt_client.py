"""
Client ChatGPT pour l'amélioration de l'IA de Léa
Utilise l'API OpenAI pour la génération de code et l'assistance intelligente
"""

import openai
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class ChatGPTClient:
    def __init__(self, api_key: str):
        """
        Initialise le client ChatGPT
        
        Args:
            api_key: Clé API OpenAI
        """
        self.client = openai.OpenAI(api_key=api_key)
        self.model = "gpt-4o"  # Utilise le modèle le plus avancé
        
    def generate_code(self, prompt: str, language: str = "python", 
                     context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Génère du code basé sur un prompt
        
        Args:
            prompt: Description de ce qui doit être généré
            language: Langage de programmation cible
            context: Contexte additionnel (ASU, historique, etc.)
            
        Returns:
            Dict contenant le code généré et les métadonnées
        """
        try:
            system_prompt = f"""Tu es Léa, un assistant de codage révolutionnaire avec des capacités uniques.
            
Tes spécialités:
- Génération de code de haute qualité en {language}
- Analyse syntaxique universelle (ASU)
- Sécurité Zero Trust et détection de vulnérabilités
- Optimisation et refactoring intelligent
- Architecture logicielle avancée

Contexte: {json.dumps(context) if context else 'Aucun contexte spécifique'}

Génère du code {language} professionnel, sécurisé et optimisé.
Inclus des commentaires explicatifs et des bonnes pratiques.
Si des vulnérabilités potentielles existent, propose des alternatives sécurisées."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            generated_code = response.choices[0].message.content
            
            return {
                "success": True,
                "code": generated_code,
                "language": language,
                "model": self.model,
                "timestamp": datetime.now().isoformat(),
                "tokens_used": response.usage.total_tokens,
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens
            }
            
        except Exception as e:
            logger.error(f"Erreur génération code ChatGPT: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def analyze_code(self, code: str, language: str = "python") -> Dict[str, Any]:
        """
        Analyse du code pour détecter des problèmes et suggérer des améliorations
        
        Args:
            code: Code source à analyser
            language: Langage de programmation
            
        Returns:
            Dict contenant l'analyse et les recommandations
        """
        try:
            system_prompt = f"""Tu es Léa, expert en analyse de code et sécurité.

Analyse ce code {language} et fournis:
1. Détection de vulnérabilités de sécurité
2. Problèmes de performance
3. Violations des bonnes pratiques
4. Suggestions d'amélioration
5. Score de qualité (0-100)
6. Refactoring recommandé

Format de réponse JSON:
{{
    "security_issues": [{{
        "type": "type_vulnérabilité",
        "severity": "low|medium|high|critical",
        "description": "description",
        "line": numéro_ligne,
        "recommendation": "solution"
    }}],
    "performance_issues": [...],
    "code_quality": {{
        "score": 85,
        "issues": [...],
        "strengths": [...]
    }},
    "refactoring_suggestions": [...],
    "overall_assessment": "évaluation globale"
}}"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Analyse ce code:\n\n```{language}\n{code}\n```"}
                ],
                temperature=0.3,
                max_tokens=1500
            )
            
            analysis_text = response.choices[0].message.content
            
            # Tenter d'extraire le JSON de la réponse
            try:
                # Chercher le JSON dans la réponse
                start_idx = analysis_text.find('{')
                end_idx = analysis_text.rfind('}') + 1
                if start_idx != -1 and end_idx != 0:
                    json_str = analysis_text[start_idx:end_idx]
                    analysis_data = json.loads(json_str)
                else:
                    analysis_data = {"raw_analysis": analysis_text}
            except json.JSONDecodeError:
                analysis_data = {"raw_analysis": analysis_text}
            
            return {
                "success": True,
                "analysis": analysis_data,
                "language": language,
                "model": self.model,
                "timestamp": datetime.now().isoformat(),
                "tokens_used": response.usage.total_tokens
            }
            
        except Exception as e:
            logger.error(f"Erreur analyse code ChatGPT: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def explain_code(self, code: str, language: str = "python") -> Dict[str, Any]:
        """
        Explique le fonctionnement d'un code
        
        Args:
            code: Code source à expliquer
            language: Langage de programmation
            
        Returns:
            Dict contenant l'explication détaillée
        """
        try:
            system_prompt = f"""Tu es Léa, expert en pédagogie du code.

Explique ce code {language} de manière claire et pédagogique:
1. Vue d'ensemble du fonctionnement
2. Explication ligne par ligne des parties complexes
3. Concepts utilisés
4. Cas d'usage typiques
5. Avantages et inconvénients

Adapte ton niveau d'explication pour être accessible tout en restant technique."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Explique ce code:\n\n```{language}\n{code}\n```"}
                ],
                temperature=0.5,
                max_tokens=1200
            )
            
            explanation = response.choices[0].message.content
            
            return {
                "success": True,
                "explanation": explanation,
                "language": language,
                "model": self.model,
                "timestamp": datetime.now().isoformat(),
                "tokens_used": response.usage.total_tokens
            }
            
        except Exception as e:
            logger.error(f"Erreur explication code ChatGPT: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def optimize_code(self, code: str, language: str = "python", 
                     optimization_type: str = "performance") -> Dict[str, Any]:
        """
        Optimise le code selon différents critères
        
        Args:
            code: Code source à optimiser
            language: Langage de programmation
            optimization_type: Type d'optimisation (performance, readability, security)
            
        Returns:
            Dict contenant le code optimisé
        """
        try:
            optimization_prompts = {
                "performance": "Optimise ce code pour les performances (vitesse d'exécution, utilisation mémoire)",
                "readability": "Optimise ce code pour la lisibilité et la maintenabilité",
                "security": "Optimise ce code pour la sécurité et la robustesse",
                "size": "Optimise ce code pour réduire sa taille tout en gardant la fonctionnalité"
            }
            
            system_prompt = f"""Tu es Léa, expert en optimisation de code.

{optimization_prompts.get(optimization_type, optimization_prompts['performance'])}

Fournis:
1. Le code optimisé
2. Explication des changements effectués
3. Gains attendus
4. Éventuels compromis

Format de réponse:
```{language}
// Code optimisé ici
```

**Changements effectués:**
- Liste des modifications

**Gains attendus:**
- Bénéfices de l'optimisation

**Compromis:**
- Éventuels inconvénients"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Code à optimiser:\n\n```{language}\n{code}\n```"}
                ],
                temperature=0.4,
                max_tokens=1500
            )
            
            optimization_result = response.choices[0].message.content
            
            return {
                "success": True,
                "optimization": optimization_result,
                "optimization_type": optimization_type,
                "language": language,
                "model": self.model,
                "timestamp": datetime.now().isoformat(),
                "tokens_used": response.usage.total_tokens
            }
            
        except Exception as e:
            logger.error(f"Erreur optimisation code ChatGPT: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def debug_code(self, code: str, error_message: str = "", 
                   language: str = "python") -> Dict[str, Any]:
        """
        Aide au débogage de code
        
        Args:
            code: Code source avec problème
            error_message: Message d'erreur (optionnel)
            language: Langage de programmation
            
        Returns:
            Dict contenant l'aide au débogage
        """
        try:
            system_prompt = f"""Tu es Léa, expert en débogage de code.

Analyse ce code {language} et aide à résoudre le problème:
1. Identifie la cause probable du problème
2. Propose une solution corrigée
3. Explique pourquoi l'erreur s'est produite
4. Donne des conseils pour éviter ce type d'erreur

Message d'erreur: {error_message if error_message else "Aucun message d'erreur fourni"}"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Code à déboguer:\n\n```{language}\n{code}\n```"}
                ],
                temperature=0.3,
                max_tokens=1200
            )
            
            debug_help = response.choices[0].message.content
            
            return {
                "success": True,
                "debug_help": debug_help,
                "language": language,
                "model": self.model,
                "timestamp": datetime.now().isoformat(),
                "tokens_used": response.usage.total_tokens
            }
            
        except Exception as e:
            logger.error(f"Erreur débogage ChatGPT: {e}")
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
            "provider": "OpenAI ChatGPT",
            "capabilities": [
                "code_generation",
                "code_analysis", 
                "code_explanation",
                "code_optimization",
                "debugging_assistance"
            ],
            "timestamp": datetime.now().isoformat()
        }

