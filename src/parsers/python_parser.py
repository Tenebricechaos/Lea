"""
Parser Python pour la conversion vers l'Arbre Syntaxique Universel
Utilise le module ast de Python pour parser le code Python et le convertir en ASU.
"""

import ast
from typing import Optional, Any, List
from src.models.ast_universal import (
    UniversalSyntaxTree, ASTNode, NodeType, DataType, SourceLocation, SourceRange,
    create_program_node, create_function_node, create_variable_node, 
    create_literal_node, create_identifier_node
)
from src.parsers.base_parser import BaseParser


class PythonParser(BaseParser):
    """Parser pour le langage Python"""
    
    def __init__(self):
        super().__init__('python')
        self.supported_extensions = ['.py', '.pyw', '.pyi']
    
    def can_parse(self, file_extension: str) -> bool:
        return file_extension.lower() in self.supported_extensions
    
    def parse(self, source_code: str, file_path: Optional[str] = None) -> UniversalSyntaxTree:
        """Parse le code Python et retourne un ASU"""
        try:
            # Parse avec le module ast de Python
            python_ast = ast.parse(source_code, filename=file_path or '<string>')
            
            # Convertit l'AST Python en ASU
            root_node = self._convert_ast_node(python_ast, file_path)
            
            # Crée l'ASU
            ust = UniversalSyntaxTree(
                root=root_node,
                metadata={
                    'language': 'python',
                    'file_path': file_path,
                    'parser': 'PythonParser',
                    'ast_version': ast.version_info if hasattr(ast, 'version_info') else None
                }
            )
            
            return ust
            
        except SyntaxError as e:
            raise ValueError(f"Erreur de syntaxe Python: {e}")
        except Exception as e:
            raise ValueError(f"Erreur lors du parsing Python: {e}")
    
    def _convert_ast_node(self, node: ast.AST, file_path: Optional[str] = None) -> ASTNode:
        """Convertit un nœud AST Python en nœud ASU"""
        
        # Détermine le type de nœud ASU
        node_type = self._get_asu_node_type(node)
        
        # Crée le nœud ASU
        asu_node = ASTNode(
            type=node_type,
            original_language='python'
        )
        
        # Ajoute les informations de localisation si disponibles
        if hasattr(node, 'lineno') and hasattr(node, 'col_offset'):
            end_line = getattr(node, 'end_lineno', node.lineno)
            end_col = getattr(node, 'end_col_offset', node.col_offset)
            
            asu_node.source_range = SourceRange(
                start=SourceLocation(node.lineno, node.col_offset, file_path),
                end=SourceLocation(end_line, end_col, file_path)
            )
        
        # Traite les attributs spécifiques selon le type de nœud
        self._process_node_attributes(node, asu_node)
        
        # Convertit les nœuds enfants
        for child in ast.iter_child_nodes(node):
            child_asu = self._convert_ast_node(child, file_path)
            asu_node.add_child(child_asu)
        
        return asu_node
    
    def _get_asu_node_type(self, node: ast.AST) -> NodeType:
        """Mappe les types de nœuds AST Python vers les types ASU"""
        mapping = {
            ast.Module: NodeType.PROGRAM,
            ast.FunctionDef: NodeType.FUNCTION_DECLARATION,
            ast.AsyncFunctionDef: NodeType.FUNCTION_DECLARATION,
            ast.ClassDef: NodeType.CLASS_DECLARATION,
            ast.Return: NodeType.RETURN_STATEMENT,
            ast.Delete: NodeType.EXPRESSION_STATEMENT,
            ast.Assign: NodeType.ASSIGNMENT_EXPRESSION,
            ast.AugAssign: NodeType.ASSIGNMENT_EXPRESSION,
            ast.AnnAssign: NodeType.VARIABLE_DECLARATION,
            ast.For: NodeType.FOR_STATEMENT,
            ast.AsyncFor: NodeType.FOR_STATEMENT,
            ast.While: NodeType.WHILE_STATEMENT,
            ast.If: NodeType.IF_STATEMENT,
            ast.With: NodeType.BLOCK_STATEMENT,
            ast.AsyncWith: NodeType.BLOCK_STATEMENT,
            ast.Raise: NodeType.EXPRESSION_STATEMENT,
            ast.Try: NodeType.BLOCK_STATEMENT,
            ast.Assert: NodeType.EXPRESSION_STATEMENT,
            ast.Import: NodeType.IMPORT_DECLARATION,
            ast.ImportFrom: NodeType.IMPORT_DECLARATION,
            ast.Global: NodeType.EXPRESSION_STATEMENT,
            ast.Nonlocal: NodeType.EXPRESSION_STATEMENT,
            ast.Expr: NodeType.EXPRESSION_STATEMENT,
            ast.Pass: NodeType.EXPRESSION_STATEMENT,
            ast.Break: NodeType.BREAK_STATEMENT,
            ast.Continue: NodeType.CONTINUE_STATEMENT,
            
            # Expressions
            ast.BoolOp: NodeType.BINARY_EXPRESSION,
            ast.BinOp: NodeType.BINARY_EXPRESSION,
            ast.UnaryOp: NodeType.UNARY_EXPRESSION,
            ast.Lambda: NodeType.FUNCTION_DECLARATION,
            ast.IfExp: NodeType.IF_STATEMENT,
            ast.Dict: NodeType.LITERAL,
            ast.Set: NodeType.LITERAL,
            ast.ListComp: NodeType.EXPRESSION_STATEMENT,
            ast.SetComp: NodeType.EXPRESSION_STATEMENT,
            ast.DictComp: NodeType.EXPRESSION_STATEMENT,
            ast.GeneratorExp: NodeType.EXPRESSION_STATEMENT,
            ast.Await: NodeType.EXPRESSION_STATEMENT,
            ast.Yield: NodeType.EXPRESSION_STATEMENT,
            ast.YieldFrom: NodeType.EXPRESSION_STATEMENT,
            ast.Compare: NodeType.BINARY_EXPRESSION,
            ast.Call: NodeType.CALL_EXPRESSION,
            ast.Constant: NodeType.LITERAL,
            ast.Attribute: NodeType.MEMBER_EXPRESSION,
            ast.Subscript: NodeType.MEMBER_EXPRESSION,
            ast.Starred: NodeType.EXPRESSION_STATEMENT,
            ast.Name: NodeType.IDENTIFIER,
            ast.List: NodeType.LITERAL,
            ast.Tuple: NodeType.LITERAL,
            ast.Slice: NodeType.EXPRESSION_STATEMENT,
        }
        
        # Gestion des anciens types pour compatibilité
        if hasattr(ast, 'Num') and isinstance(node, ast.Num):
            return NodeType.LITERAL
        if hasattr(ast, 'Str') and isinstance(node, ast.Str):
            return NodeType.LITERAL
        if hasattr(ast, 'Bytes') and isinstance(node, ast.Bytes):
            return NodeType.LITERAL
        if hasattr(ast, 'NameConstant') and isinstance(node, ast.NameConstant):
            return NodeType.LITERAL
        
        return mapping.get(type(node), NodeType.EXPRESSION_STATEMENT)
    
    def _process_node_attributes(self, ast_node: ast.AST, asu_node: ASTNode) -> None:
        """Traite les attributs spécifiques d'un nœud AST Python"""
        
        if isinstance(ast_node, ast.Module):
            asu_node.set_attribute('type', 'module')
        
        elif isinstance(ast_node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            asu_node.set_attribute('name', ast_node.name)
            asu_node.set_attribute('is_async', isinstance(ast_node, ast.AsyncFunctionDef))
            
            # Arguments de la fonction
            args = []
            if ast_node.args:
                for arg in ast_node.args.args:
                    args.append(arg.arg)
            asu_node.set_attribute('parameters', args)
            
            # Décorateurs
            if ast_node.decorator_list:
                decorators = []
                for decorator in ast_node.decorator_list:
                    if isinstance(decorator, ast.Name):
                        decorators.append(decorator.id)
                    elif isinstance(decorator, ast.Attribute):
                        decorators.append(f"{decorator.attr}")
                asu_node.set_attribute('decorators', decorators)
        
        elif isinstance(ast_node, ast.ClassDef):
            asu_node.set_attribute('name', ast_node.name)
            
            # Classes de base
            bases = []
            for base in ast_node.bases:
                if isinstance(base, ast.Name):
                    bases.append(base.id)
            asu_node.set_attribute('base_classes', bases)
            
            # Décorateurs
            if ast_node.decorator_list:
                decorators = []
                for decorator in ast_node.decorator_list:
                    if isinstance(decorator, ast.Name):
                        decorators.append(decorator.id)
                asu_node.set_attribute('decorators', decorators)
        
        elif isinstance(ast_node, ast.Name):
            asu_node.set_attribute('name', ast_node.id)
            asu_node.set_attribute('context', type(ast_node.ctx).__name__)
        
        elif isinstance(ast_node, ast.Constant):
            asu_node.set_attribute('value', ast_node.value)
            asu_node.set_attribute('data_type', self._get_python_type(ast_node.value))
        
        elif hasattr(ast, 'Num') and isinstance(ast_node, ast.Num):
            asu_node.set_attribute('value', ast_node.n)
            asu_node.set_attribute('data_type', DataType.NUMBER.value)
        
        elif hasattr(ast, 'Str') and isinstance(ast_node, ast.Str):
            asu_node.set_attribute('value', ast_node.s)
            asu_node.set_attribute('data_type', DataType.STRING.value)
        
        elif isinstance(ast_node, ast.BinOp):
            asu_node.set_attribute('operator', type(ast_node.op).__name__)
        
        elif isinstance(ast_node, ast.UnaryOp):
            asu_node.set_attribute('operator', type(ast_node.op).__name__)
        
        elif isinstance(ast_node, ast.Call):
            if isinstance(ast_node.func, ast.Name):
                asu_node.set_attribute('function_name', ast_node.func.id)
            elif isinstance(ast_node.func, ast.Attribute):
                asu_node.set_attribute('function_name', ast_node.func.attr)
        
        elif isinstance(ast_node, ast.Attribute):
            asu_node.set_attribute('attribute', ast_node.attr)
        
        elif isinstance(ast_node, (ast.Import, ast.ImportFrom)):
            if isinstance(ast_node, ast.ImportFrom):
                asu_node.set_attribute('module', ast_node.module)
                asu_node.set_attribute('level', ast_node.level)
            
            names = []
            for alias in ast_node.names:
                name_info = {'name': alias.name}
                if alias.asname:
                    name_info['alias'] = alias.asname
                names.append(name_info)
            asu_node.set_attribute('names', names)
    
    def _get_python_type(self, value: Any) -> str:
        """Détermine le type de données d'une valeur Python"""
        if isinstance(value, str):
            return DataType.STRING.value
        elif isinstance(value, int):
            return DataType.INTEGER.value
        elif isinstance(value, float):
            return DataType.FLOAT.value
        elif isinstance(value, bool):
            return DataType.BOOLEAN.value
        elif value is None:
            return DataType.NULL.value
        else:
            return DataType.ANY.value

