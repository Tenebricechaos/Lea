"""
Moteur IA Hybride de Léa
Combine ChatGPT, DeepSeek et l'ASU pour une intelligence artificielle révolutionnaire
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from .chatgpt_client import ChatGPTClient
from .deepseek_client import DeepSeekClient
# Import temporairement commenté pour éviter l'erreur
# from ..models.ast_universal import ASTUniversal

logger = logging.getLogger(__name__)

class HybridAIEngine:
    def __init__(self, chatgpt_api_key: str, deepseek_api_key: str):
        """
        Initialise le moteur IA hybride
        
        Args:
            chatgpt_api_key: Clé API ChatGPT
            deepseek_api_key: Clé API DeepSeek
        """
        self.chatgpt = ChatGPTClient(chatgpt_api_key)
        self.deepseek = DeepSeekClient(deepseek_api_key)
        # ASU temporairement désactivé
        # self.asu = ASTUniversal()
        
        # Configuration des capacités de chaque IA
        self.ai_capabilities = {
            "chatgpt": {
                "strengths": ["code_generation", "explanation", "debugging", "quick_analysis"],
                "speed": "fast",
                "cost": "medium"
            },
            "deepseek": {
                "strengths": ["deep_analysis", "architecture", "optimization", "complex_reasoning"],
                "speed": "medium",
                "cost": "low"
            },
            "asu": {
                "strengths": ["syntax_analysis", "structure_understanding", "pattern_detection"],
                "speed": "very_fast",
                "cost": "free"
            }
        }
        
        self.executor = ThreadPoolExecutor(max_workers=3)
    
    def _select_best_ai(self, task_type: str, complexity: str = "medium") -> List[str]:
        """
        Sélectionne la meilleure IA pour une tâche donnée
        
        Args:
            task_type: Type de tâche
            complexity: Niveau de complexité
            
        Returns:
            Liste des IAs recommandées par ordre de priorité
        """
        task_mapping = {
            "code_generation": {
                "simple": ["chatgpt", "asu"],
                "medium": ["chatgpt", "deepseek"],
                "complex": ["deepseek", "chatgpt"]
            },
            "code_analysis": {
                "simple": ["asu", "chatgpt"],
                "medium": ["chatgpt", "asu", "deepseek"],
                "complex": ["deepseek", "chatgpt", "asu"]
            },
            "architecture_design": {
                "simple": ["chatgpt", "deepseek"],
                "medium": ["deepseek", "chatgpt"],
                "complex": ["deepseek"]
            },
            "debugging": {
                "simple": ["chatgpt", "asu"],
                "medium": ["chatgpt", "deepseek"],
                "complex": ["deepseek", "chatgpt"]
            },
            "optimization": {
                "simple": ["chatgpt", "asu"],
                "medium": ["deepseek", "chatgpt"],
                "complex": ["deepseek"]
            },
            "explanation": {
                "simple": ["chatgpt"],
                "medium": ["chatgpt", "deepseek"],
                "complex": ["chatgpt", "deepseek"]
            }
        }
        
        return task_mapping.get(task_type, {}).get(complexity, ["chatgpt", "deepseek", "asu"])
    
    def _combine_results(self, results: List[Dict], task_type: str) -> Dict[str, Any]:
        """
        Combine les résultats de plusieurs IAs
        
        Args:
            results: Liste des résultats des différentes IAs
            task_type: Type de tâche
            
        Returns:
            Résultat combiné optimisé
        """
        successful_results = [r for r in results if r.get("success", False)]
        
        if not successful_results:
            return {
                "success": False,
                "error": "Aucune IA n'a pu traiter la demande",
                "timestamp": datetime.now().isoformat()
            }
        
        # Stratégies de combinaison selon le type de tâche
        if task_type == "code_analysis":
            return self._combine_analysis_results(successful_results)
        elif task_type == "code_generation":
            return self._combine_generation_results(successful_results)
        elif task_type == "architecture_design":
            return self._combine_architecture_results(successful_results)
        else:
            # Stratégie par défaut: prendre le meilleur résultat
            return self._select_best_result(successful_results)
    
    def _combine_analysis_results(self, results: List[Dict]) -> Dict[str, Any]:
        """Combine les résultats d'analyse de code"""
        combined = {
            "success": True,
            "analysis_type": "hybrid",
            "sources": [],
            "comprehensive_analysis": {},
            "timestamp": datetime.now().isoformat()
        }
        
        for result in results:
            source = result.get("model", "unknown")
            combined["sources"].append(source)
            
            if "analysis" in result:
                combined["comprehensive_analysis"][source] = result["analysis"]
            elif "deep_analysis" in result:
                combined["comprehensive_analysis"][source] = result["deep_analysis"]
            elif "asu_analysis" in result:
                combined["comprehensive_analysis"][source] = result["asu_analysis"]
        
        # Synthèse des analyses
        combined["synthesis"] = self._synthesize_analyses(combined["comprehensive_analysis"])
        
        return combined
    
    def _combine_generation_results(self, results: List[Dict]) -> Dict[str, Any]:
        """Combine les résultats de génération de code"""
        # Prendre le meilleur résultat basé sur la qualité estimée
        best_result = max(results, key=lambda r: self._estimate_code_quality(r))
        
        # Ajouter les alternatives
        alternatives = [r for r in results if r != best_result]
        
        return {
            "success": True,
            "primary_code": best_result.get("code", ""),
            "alternatives": [r.get("code", "") for r in alternatives],
            "sources": [r.get("model", "unknown") for r in results],
            "quality_score": self._estimate_code_quality(best_result),
            "timestamp": datetime.now().isoformat()
        }
    
    def _combine_architecture_results(self, results: List[Dict]) -> Dict[str, Any]:
        """Combine les résultats de conception d'architecture"""
        return {
            "success": True,
            "architecture_proposals": [r.get("architecture", "") for r in results],
            "sources": [r.get("model", "unknown") for r in results],
            "recommended": results[0].get("architecture", "") if results else "",
            "timestamp": datetime.now().isoformat()
        }
    
    def _select_best_result(self, results: List[Dict]) -> Dict[str, Any]:
        """Sélectionne le meilleur résultat"""
        # Logique de sélection basée sur la qualité et la complétude
        best = max(results, key=lambda r: len(str(r.get("content", ""))))
        best["hybrid_processing"] = True
        best["alternatives_count"] = len(results) - 1
        return best
    
    def _synthesize_analyses(self, analyses: Dict[str, Any]) -> str:
        """Synthétise plusieurs analyses en une vue unifiée"""
        synthesis = "## Synthèse des Analyses\n\n"
        
        # Combiner les points clés de chaque analyse
        for source, analysis in analyses.items():
            synthesis += f"### Analyse {source}:\n"
            if isinstance(analysis, dict):
                for key, value in analysis.items():
                    synthesis += f"- **{key}**: {value}\n"
            else:
                synthesis += f"{analysis}\n"
            synthesis += "\n"
        
        return synthesis
    
    def _estimate_code_quality(self, result: Dict) -> float:
        """Estime la qualité d'un code généré"""
        code = result.get("code", "")
        if not code:
            return 0.0
        
        quality_score = 0.0
        
        # Facteurs de qualité
        if "class" in code.lower():
            quality_score += 0.2
        if "def " in code or "function" in code:
            quality_score += 0.2
        if "try:" in code or "except" in code:
            quality_score += 0.1
        if "import" in code:
            quality_score += 0.1
        if len(code.split('\n')) > 10:
            quality_score += 0.2
        if "# " in code or '"""' in code:
            quality_score += 0.2
        
        return min(quality_score, 1.0)
    
    async def intelligent_code_generation(self, prompt: str, language: str = "python",
                                        complexity: str = "medium",
                                        use_parallel: bool = True) -> Dict[str, Any]:
        """
        Génération de code intelligente utilisant le meilleur moteur IA
        
        Args:
            prompt: Description du code à générer
            language: Langage de programmation
            complexity: Niveau de complexité
            use_parallel: Utiliser le traitement parallèle
            
        Returns:
            Code généré avec métadonnées
        """
        try:
            selected_ais = self._select_best_ai("code_generation", complexity)
            
            if use_parallel and len(selected_ais) > 1:
                # Traitement parallèle
                futures = []
                
                for ai_name in selected_ais[:2]:  # Limiter à 2 pour éviter les coûts
                    if ai_name == "chatgpt":
                        future = self.executor.submit(
                            self.chatgpt.generate_code, prompt, language
                        )
                    elif ai_name == "deepseek":
                        future = self.executor.submit(
                            self.deepseek.advanced_code_generation, prompt, language
                        )
                    futures.append((ai_name, future))
                
                results = []
                for ai_name, future in futures:
                    try:
                        result = future.result(timeout=30)
                        result["ai_source"] = ai_name
                        results.append(result)
                    except Exception as e:
                        logger.error(f"Erreur {ai_name}: {e}")
                
                return self._combine_generation_results(results)
            
            else:
                # Traitement séquentiel avec la meilleure IA
                best_ai = selected_ais[0]
                
                if best_ai == "chatgpt":
                    result = self.chatgpt.generate_code(prompt, language)
                elif best_ai == "deepseek":
                    result = self.deepseek.advanced_code_generation(prompt, language)
                else:
                    result = {"success": False, "error": "IA non supportée"}
                
                result["ai_source"] = best_ai
                result["hybrid_processing"] = False
                return result
                
        except Exception as e:
            logger.error(f"Erreur génération code hybride: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def comprehensive_code_analysis(self, code: str, language: str = "python",
                                        include_asu: bool = True) -> Dict[str, Any]:
        """
        Analyse complète de code utilisant tous les moteurs IA
        
        Args:
            code: Code source à analyser
            language: Langage de programmation
            include_asu: Inclure l'analyse ASU
            
        Returns:
            Analyse complète combinée
        """
        try:
            futures = []
            
            # ChatGPT pour l'analyse rapide
            future_chatgpt = self.executor.submit(
                self.chatgpt.analyze_code, code, language
            )
            futures.append(("chatgpt", future_chatgpt))
            
            # DeepSeek pour l'analyse approfondie
            future_deepseek = self.executor.submit(
                self.deepseek.deep_code_analysis, code, language
            )
            futures.append(("deepseek", future_deepseek))
            
            # ASU pour l'analyse structurelle
            if include_asu:
                try:
                    # ASU temporairement désactivé
                    # asu_result = self.asu.parse_code(code, language)
                    # if asu_result.get("success"):
                    #     asu_analysis = {
                    #         "success": True,
                    #         "asu_analysis": {
                    #             "structure": asu_result.get("ast", {}),
                    #             "metrics": asu_result.get("metrics", {}),
                    #             "patterns": asu_result.get("patterns", [])
                    #         },
                    #         "model": "ASU",
                    #         "timestamp": datetime.now().isoformat()
                    #     }
                    #     futures.append(("asu", lambda: asu_analysis))
                    pass
                except Exception as e:
                    logger.error(f"Erreur ASU: {e}")
            
            # Collecter les résultats
            results = []
            for ai_name, future in futures:
                try:
                    if callable(future):
                        result = future()
                    else:
                        result = future.result(timeout=45)
                    result["ai_source"] = ai_name
                    results.append(result)
                except Exception as e:
                    logger.error(f"Erreur {ai_name}: {e}")
            
            return self._combine_analysis_results(results)
            
        except Exception as e:
            logger.error(f"Erreur analyse complète: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def intelligent_debugging(self, code: str, error_message: str = "",
                                  language: str = "python") -> Dict[str, Any]:
        """
        Débogage intelligent utilisant plusieurs IAs
        
        Args:
            code: Code avec problème
            error_message: Message d'erreur
            language: Langage de programmation
            
        Returns:
            Aide au débogage complète
        """
        try:
            # Utiliser ChatGPT pour le débogage rapide
            chatgpt_result = self.chatgpt.debug_code(code, error_message, language)
            
            # Si le problème semble complexe, utiliser aussi DeepSeek
            if "complex" in error_message.lower() or len(code) > 1000:
                deepseek_result = self.deepseek.complex_problem_solving(
                    f"Debug this {language} code with error: {error_message}\n\nCode:\n{code}"
                )
                
                return {
                    "success": True,
                    "quick_debug": chatgpt_result.get("debug_help", ""),
                    "deep_analysis": deepseek_result.get("solution", ""),
                    "sources": ["chatgpt", "deepseek"],
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return chatgpt_result
                
        except Exception as e:
            logger.error(f"Erreur débogage intelligent: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def smart_optimization(self, code: str, language: str = "python",
                               optimization_goals: List[str] = None) -> Dict[str, Any]:
        """
        Optimisation intelligente de code
        
        Args:
            code: Code à optimiser
            language: Langage de programmation
            optimization_goals: Objectifs d'optimisation
            
        Returns:
            Code optimisé avec explications
        """
        try:
            if optimization_goals is None:
                optimization_goals = ["performance"]
            
            # Utiliser DeepSeek pour l'optimisation avancée
            deepseek_result = self.deepseek.performance_optimization(
                code, language, optimization_goals
            )
            
            # Utiliser ChatGPT pour des optimisations complémentaires
            chatgpt_result = self.chatgpt.optimize_code(
                code, language, optimization_goals[0] if optimization_goals else "performance"
            )
            
            return {
                "success": True,
                "advanced_optimization": deepseek_result.get("optimization", ""),
                "quick_optimization": chatgpt_result.get("optimization", ""),
                "goals": optimization_goals,
                "sources": ["deepseek", "chatgpt"],
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erreur optimisation intelligente: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_engine_stats(self) -> Dict[str, Any]:
        """
        Retourne les statistiques du moteur hybride
        
        Returns:
            Statistiques complètes
        """
        return {
            "engine_type": "Hybrid AI Engine",
            "components": {
                "chatgpt": self.chatgpt.get_usage_stats(),
                "deepseek": self.deepseek.get_usage_stats(),
                "asu": {"provider": "Internal ASU", "capabilities": ["syntax_analysis"]}
            },
            "capabilities": [
                "intelligent_code_generation",
                "comprehensive_code_analysis", 
                "intelligent_debugging",
                "smart_optimization",
                "hybrid_reasoning"
            ],
            "advantages": [
                "Multi-AI approach for better results",
                "Automatic AI selection based on task complexity",
                "Parallel processing for faster results",
                "Cost optimization through intelligent routing"
            ],
            "timestamp": datetime.now().isoformat()
        }

