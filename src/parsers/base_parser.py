"""
Parser de base pour la conversion vers l'Arbre Syntaxique Universel
Ce module définit l'interface commune pour tous les parsers de langages spécifiques.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from src.models.ast_universal import UniversalSyntaxTree, ASTNode, NodeType, create_program_node


class BaseParser(ABC):
    """Classe de base pour tous les parsers de langages"""
    
    def __init__(self, language: str):
        self.language = language
        self.supported_extensions = []
    
    @abstractmethod
    def parse(self, source_code: str, file_path: Optional[str] = None) -> UniversalSyntaxTree:
        """
        Parse le code source et retourne un ASU
        
        Args:
            source_code: Le code source à parser
            file_path: Chemin du fichier source (optionnel)
            
        Returns:
            UniversalSyntaxTree: L'arbre syntaxique universel
        """
        pass
    
    @abstractmethod
    def can_parse(self, file_extension: str) -> bool:
        """
        Vérifie si ce parser peut traiter un fichier avec cette extension
        
        Args:
            file_extension: Extension du fichier (ex: '.py', '.js')
            
        Returns:
            bool: True si le parser peut traiter ce type de fichier
        """
        pass
    
    def get_language_info(self) -> Dict[str, Any]:
        """Retourne les informations sur le langage supporté"""
        return {
            'name': self.language,
            'extensions': self.supported_extensions,
            'parser_version': '1.0'
        }


class ParserRegistry:
    """Registre des parsers disponibles"""
    
    def __init__(self):
        self._parsers: Dict[str, BaseParser] = {}
        self._extension_map: Dict[str, str] = {}
    
    def register_parser(self, parser: BaseParser) -> None:
        """Enregistre un nouveau parser"""
        self._parsers[parser.language] = parser
        
        # Met à jour la carte des extensions
        for ext in parser.supported_extensions:
            self._extension_map[ext] = parser.language
    
    def get_parser(self, language: str) -> Optional[BaseParser]:
        """Récupère un parser par nom de langage"""
        return self._parsers.get(language)
    
    def get_parser_by_extension(self, file_extension: str) -> Optional[BaseParser]:
        """Récupère un parser par extension de fichier"""
        language = self._extension_map.get(file_extension.lower())
        if language:
            return self._parsers.get(language)
        return None
    
    def list_supported_languages(self) -> List[str]:
        """Liste tous les langages supportés"""
        return list(self._parsers.keys())
    
    def list_supported_extensions(self) -> List[str]:
        """Liste toutes les extensions supportées"""
        return list(self._extension_map.keys())


# Instance globale du registre
parser_registry = ParserRegistry()


def parse_code(source_code: str, language: Optional[str] = None, 
               file_path: Optional[str] = None) -> UniversalSyntaxTree:
    """
    Parse du code source en détectant automatiquement le langage si nécessaire
    
    Args:
        source_code: Le code source à parser
        language: Langage spécifique (optionnel)
        file_path: Chemin du fichier pour détecter le langage (optionnel)
        
    Returns:
        UniversalSyntaxTree: L'arbre syntaxique universel
        
    Raises:
        ValueError: Si aucun parser approprié n'est trouvé
    """
    parser = None
    
    if language:
        parser = parser_registry.get_parser(language)
    elif file_path:
        # Détection par extension de fichier
        import os
        _, ext = os.path.splitext(file_path)
        parser = parser_registry.get_parser_by_extension(ext)
    
    if not parser:
        raise ValueError(f"Aucun parser trouvé pour le langage '{language}' ou le fichier '{file_path}'")
    
    return parser.parse(source_code, file_path)


def detect_language(source_code: str, file_path: Optional[str] = None) -> Optional[str]:
    """
    Détecte le langage de programmation du code source
    
    Args:
        source_code: Le code source à analyser
        file_path: Chemin du fichier (optionnel)
        
    Returns:
        str: Le langage détecté ou None si non détecté
    """
    # Détection par extension de fichier en premier
    if file_path:
        import os
        _, ext = os.path.splitext(file_path)
        if ext.lower() in parser_registry.list_supported_extensions():
            return parser_registry._extension_map[ext.lower()]
    
    # Détection par analyse du contenu (heuristiques simples)
    source_lower = source_code.lower().strip()
    
    # Python
    if any(keyword in source_lower for keyword in ['def ', 'import ', 'from ', 'class ', 'if __name__']):
        return 'python'
    
    # JavaScript/TypeScript
    if any(keyword in source_lower for keyword in ['function ', 'const ', 'let ', 'var ', '=>', 'console.log']):
        return 'javascript'
    
    # Java
    if any(keyword in source_lower for keyword in ['public class', 'public static void main', 'import java']):
        return 'java'
    
    # C/C++
    if any(keyword in source_lower for keyword in ['#include', 'int main(', 'printf(', 'cout <<']):
        return 'c' if 'cout' not in source_lower else 'cpp'
    
    return None

