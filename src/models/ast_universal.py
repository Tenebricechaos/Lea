"""
Modèle pour l'Arbre Syntaxique Universel (ASU) de Léa
Ce module définit la structure de données pour représenter le code de tous les langages
de programmation de manière uniforme.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from enum import Enum
import json
import uuid


class NodeType(Enum):
    """Types de nœuds dans l'ASU"""
    # Nœuds de base
    PROGRAM = "program"
    MODULE = "module"
    
    # Déclarations
    VARIABLE_DECLARATION = "variable_declaration"
    FUNCTION_DECLARATION = "function_declaration"
    CLASS_DECLARATION = "class_declaration"
    INTERFACE_DECLARATION = "interface_declaration"
    IMPORT_DECLARATION = "import_declaration"
    
    # Expressions
    LITERAL = "literal"
    IDENTIFIER = "identifier"
    BINARY_EXPRESSION = "binary_expression"
    UNARY_EXPRESSION = "unary_expression"
    CALL_EXPRESSION = "call_expression"
    MEMBER_EXPRESSION = "member_expression"
    ASSIGNMENT_EXPRESSION = "assignment_expression"
    
    # Statements
    EXPRESSION_STATEMENT = "expression_statement"
    BLOCK_STATEMENT = "block_statement"
    IF_STATEMENT = "if_statement"
    WHILE_STATEMENT = "while_statement"
    FOR_STATEMENT = "for_statement"
    RETURN_STATEMENT = "return_statement"
    BREAK_STATEMENT = "break_statement"
    CONTINUE_STATEMENT = "continue_statement"
    
    # Types de données
    PRIMITIVE_TYPE = "primitive_type"
    ARRAY_TYPE = "array_type"
    OBJECT_TYPE = "object_type"
    FUNCTION_TYPE = "function_type"
    
    # Commentaires et métadonnées
    COMMENT = "comment"
    ANNOTATION = "annotation"


class DataType(Enum):
    """Types de données primitifs supportés"""
    STRING = "string"
    NUMBER = "number"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    NULL = "null"
    UNDEFINED = "undefined"
    VOID = "void"
    ANY = "any"


@dataclass
class SourceLocation:
    """Localisation dans le code source original"""
    line: int
    column: int
    file_path: Optional[str] = None


@dataclass
class SourceRange:
    """Plage de localisation dans le code source"""
    start: SourceLocation
    end: SourceLocation


@dataclass
class ASTNode:
    """Nœud de base de l'Arbre Syntaxique Universel"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: NodeType = NodeType.PROGRAM
    children: List['ASTNode'] = field(default_factory=list)
    attributes: Dict[str, Any] = field(default_factory=dict)
    source_range: Optional[SourceRange] = None
    original_language: Optional[str] = None
    
    def add_child(self, child: 'ASTNode') -> None:
        """Ajoute un nœud enfant"""
        self.children.append(child)
    
    def get_attribute(self, key: str, default: Any = None) -> Any:
        """Récupère un attribut"""
        return self.attributes.get(key, default)
    
    def set_attribute(self, key: str, value: Any) -> None:
        """Définit un attribut"""
        self.attributes[key] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit le nœud en dictionnaire pour sérialisation"""
        return {
            'id': self.id,
            'type': self.type.value,
            'children': [child.to_dict() for child in self.children],
            'attributes': self.attributes,
            'source_range': {
                'start': {
                    'line': self.source_range.start.line,
                    'column': self.source_range.start.column,
                    'file_path': self.source_range.start.file_path
                },
                'end': {
                    'line': self.source_range.end.line,
                    'column': self.source_range.end.column,
                    'file_path': self.source_range.end.file_path
                }
            } if self.source_range else None,
            'original_language': self.original_language
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ASTNode':
        """Crée un nœud à partir d'un dictionnaire"""
        node = cls(
            id=data['id'],
            type=NodeType(data['type']),
            attributes=data.get('attributes', {}),
            original_language=data.get('original_language')
        )
        
        if data.get('source_range'):
            sr = data['source_range']
            node.source_range = SourceRange(
                start=SourceLocation(
                    line=sr['start']['line'],
                    column=sr['start']['column'],
                    file_path=sr['start'].get('file_path')
                ),
                end=SourceLocation(
                    line=sr['end']['line'],
                    column=sr['end']['column'],
                    file_path=sr['end'].get('file_path')
                )
            )
        
        node.children = [cls.from_dict(child) for child in data.get('children', [])]
        return node


@dataclass
class UniversalSyntaxTree:
    """Arbre Syntaxique Universel complet"""
    root: ASTNode
    metadata: Dict[str, Any] = field(default_factory=dict)
    version: str = "1.0"
    
    def to_json(self) -> str:
        """Sérialise l'ASU en JSON"""
        return json.dumps({
            'version': self.version,
            'metadata': self.metadata,
            'root': self.root.to_dict()
        }, indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'UniversalSyntaxTree':
        """Désérialise l'ASU depuis JSON"""
        data = json.loads(json_str)
        return cls(
            root=ASTNode.from_dict(data['root']),
            metadata=data.get('metadata', {}),
            version=data.get('version', '1.0')
        )
    
    def get_nodes_by_type(self, node_type: NodeType) -> List[ASTNode]:
        """Récupère tous les nœuds d'un type donné"""
        result = []
        
        def traverse(node: ASTNode):
            if node.type == node_type:
                result.append(node)
            for child in node.children:
                traverse(child)
        
        traverse(self.root)
        return result
    
    def find_node_by_id(self, node_id: str) -> Optional[ASTNode]:
        """Trouve un nœud par son ID"""
        def traverse(node: ASTNode) -> Optional[ASTNode]:
            if node.id == node_id:
                return node
            for child in node.children:
                result = traverse(child)
                if result:
                    return result
            return None
        
        return traverse(self.root)


# Fonctions utilitaires pour créer des nœuds spécifiques

def create_program_node(language: str) -> ASTNode:
    """Crée un nœud programme racine"""
    node = ASTNode(type=NodeType.PROGRAM, original_language=language)
    node.set_attribute('language', language)
    return node


def create_function_node(name: str, parameters: List[str], return_type: Optional[str] = None) -> ASTNode:
    """Crée un nœud fonction"""
    node = ASTNode(type=NodeType.FUNCTION_DECLARATION)
    node.set_attribute('name', name)
    node.set_attribute('parameters', parameters)
    if return_type:
        node.set_attribute('return_type', return_type)
    return node


def create_variable_node(name: str, var_type: Optional[str] = None, value: Any = None) -> ASTNode:
    """Crée un nœud variable"""
    node = ASTNode(type=NodeType.VARIABLE_DECLARATION)
    node.set_attribute('name', name)
    if var_type:
        node.set_attribute('type', var_type)
    if value is not None:
        node.set_attribute('value', value)
    return node


def create_literal_node(value: Any, data_type: DataType) -> ASTNode:
    """Crée un nœud littéral"""
    node = ASTNode(type=NodeType.LITERAL)
    node.set_attribute('value', value)
    node.set_attribute('data_type', data_type.value)
    return node


def create_identifier_node(name: str) -> ASTNode:
    """Crée un nœud identifiant"""
    node = ASTNode(type=NodeType.IDENTIFIER)
    node.set_attribute('name', name)
    return node

