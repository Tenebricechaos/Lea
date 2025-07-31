"""
Parser JavaScript pour la conversion vers l'Arbre Syntaxique Universel
Utilise une approche basée sur des expressions régulières et une analyse lexicale simple
pour parser le code JavaScript et le convertir en ASU.
"""

import re
from typing import Optional, List, Dict, Any, Tuple
from src.models.ast_universal import (
    UniversalSyntaxTree, ASTNode, NodeType, DataType, SourceLocation, SourceRange,
    create_program_node, create_function_node, create_variable_node, 
    create_literal_node, create_identifier_node
)
from src.parsers.base_parser import BaseParser


class Token:
    """Représente un token dans le code JavaScript"""
    def __init__(self, type_: str, value: str, line: int, column: int):
        self.type = type_
        self.value = value
        self.line = line
        self.column = column


class JavaScriptParser(BaseParser):
    """Parser pour le langage JavaScript"""
    
    def __init__(self):
        super().__init__('javascript')
        self.supported_extensions = ['.js', '.jsx', '.mjs', '.ts', '.tsx']
        
        # Patterns pour la tokenisation
        self.token_patterns = [
            ('COMMENT_SINGLE', r'//.*'),
            ('COMMENT_MULTI', r'/\*[\s\S]*?\*/'),
            ('STRING_DOUBLE', r'"(?:[^"\\]|\\.)*"'),
            ('STRING_SINGLE', r"'(?:[^'\\]|\\.)*'"),
            ('STRING_TEMPLATE', r'`(?:[^`\\]|\\.)*`'),
            ('NUMBER', r'\d+\.?\d*'),
            ('FUNCTION', r'\bfunction\b'),
            ('CONST', r'\bconst\b'),
            ('LET', r'\blet\b'),
            ('VAR', r'\bvar\b'),
            ('IF', r'\bif\b'),
            ('ELSE', r'\belse\b'),
            ('FOR', r'\bfor\b'),
            ('WHILE', r'\bwhile\b'),
            ('RETURN', r'\breturn\b'),
            ('BREAK', r'\bbreak\b'),
            ('CONTINUE', r'\bcontinue\b'),
            ('CLASS', r'\bclass\b'),
            ('IMPORT', r'\bimport\b'),
            ('EXPORT', r'\bexport\b'),
            ('FROM', r'\bfrom\b'),
            ('TRUE', r'\btrue\b'),
            ('FALSE', r'\bfalse\b'),
            ('NULL', r'\bnull\b'),
            ('UNDEFINED', r'\bundefined\b'),
            ('ARROW', r'=>'),
            ('ASSIGN', r'='),
            ('PLUS_ASSIGN', r'\+='),
            ('MINUS_ASSIGN', r'-='),
            ('MULTIPLY_ASSIGN', r'\*='),
            ('DIVIDE_ASSIGN', r'/='),
            ('EQUALITY', r'===|=='),
            ('INEQUALITY', r'!==|!='),
            ('LESS_EQUAL', r'<='),
            ('GREATER_EQUAL', r'>='),
            ('LESS', r'<'),
            ('GREATER', r'>'),
            ('PLUS', r'\+'),
            ('MINUS', r'-'),
            ('MULTIPLY', r'\*'),
            ('DIVIDE', r'/'),
            ('MODULO', r'%'),
            ('AND', r'&&'),
            ('OR', r'\|\|'),
            ('NOT', r'!'),
            ('SEMICOLON', r';'),
            ('COMMA', r','),
            ('DOT', r'\.'),
            ('LPAREN', r'\('),
            ('RPAREN', r'\)'),
            ('LBRACE', r'\{'),
            ('RBRACE', r'\}'),
            ('LBRACKET', r'\['),
            ('RBRACKET', r'\]'),
            ('IDENTIFIER', r'[a-zA-Z_$][a-zA-Z0-9_$]*'),
            ('WHITESPACE', r'\s+'),
            ('NEWLINE', r'\n'),
        ]
        
        self.compiled_patterns = [(name, re.compile(pattern)) for name, pattern in self.token_patterns]
    
    def can_parse(self, file_extension: str) -> bool:
        return file_extension.lower() in self.supported_extensions
    
    def parse(self, source_code: str, file_path: Optional[str] = None) -> UniversalSyntaxTree:
        """Parse le code JavaScript et retourne un ASU"""
        try:
            # Tokenise le code
            tokens = self._tokenize(source_code)
            
            # Parse les tokens en ASU
            root_node = self._parse_tokens(tokens, file_path)
            
            # Crée l'ASU
            ust = UniversalSyntaxTree(
                root=root_node,
                metadata={
                    'language': 'javascript',
                    'file_path': file_path,
                    'parser': 'JavaScriptParser',
                    'token_count': len(tokens)
                }
            )
            
            return ust
            
        except Exception as e:
            raise ValueError(f"Erreur lors du parsing JavaScript: {e}")
    
    def _tokenize(self, source_code: str) -> List[Token]:
        """Tokenise le code JavaScript"""
        tokens = []
        lines = source_code.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            column = 0
            while column < len(line):
                matched = False
                
                for token_type, pattern in self.compiled_patterns:
                    match = pattern.match(line, column)
                    if match:
                        value = match.group(0)
                        
                        # Ignore les espaces et commentaires pour le parsing
                        if token_type not in ['WHITESPACE', 'COMMENT_SINGLE', 'COMMENT_MULTI']:
                            tokens.append(Token(token_type, value, line_num, column))
                        
                        column = match.end()
                        matched = True
                        break
                
                if not matched:
                    # Caractère non reconnu, on l'ignore ou on lève une erreur
                    column += 1
        
        return tokens
    
    def _parse_tokens(self, tokens: List[Token], file_path: Optional[str] = None) -> ASTNode:
        """Parse les tokens en ASU"""
        root = ASTNode(type=NodeType.PROGRAM, original_language='javascript')
        root.set_attribute('language', 'javascript')
        
        i = 0
        while i < len(tokens):
            node, consumed = self._parse_statement(tokens, i, file_path)
            if node:
                root.add_child(node)
            i += consumed if consumed > 0 else 1
        
        return root
    
    def _parse_statement(self, tokens: List[Token], start: int, file_path: Optional[str] = None) -> Tuple[Optional[ASTNode], int]:
        """Parse une instruction JavaScript"""
        if start >= len(tokens):
            return None, 0
        
        token = tokens[start]
        
        # Déclaration de fonction
        if token.type == 'FUNCTION':
            return self._parse_function_declaration(tokens, start, file_path)
        
        # Déclarations de variables
        elif token.type in ['CONST', 'LET', 'VAR']:
            return self._parse_variable_declaration(tokens, start, file_path)
        
        # Instruction if
        elif token.type == 'IF':
            return self._parse_if_statement(tokens, start, file_path)
        
        # Boucles
        elif token.type == 'FOR':
            return self._parse_for_statement(tokens, start, file_path)
        elif token.type == 'WHILE':
            return self._parse_while_statement(tokens, start, file_path)
        
        # Instructions de contrôle
        elif token.type == 'RETURN':
            return self._parse_return_statement(tokens, start, file_path)
        elif token.type == 'BREAK':
            return self._parse_break_statement(tokens, start, file_path)
        elif token.type == 'CONTINUE':
            return self._parse_continue_statement(tokens, start, file_path)
        
        # Déclaration de classe
        elif token.type == 'CLASS':
            return self._parse_class_declaration(tokens, start, file_path)
        
        # Import/Export
        elif token.type in ['IMPORT', 'EXPORT']:
            return self._parse_import_export(tokens, start, file_path)
        
        # Expression statement
        else:
            return self._parse_expression_statement(tokens, start, file_path)
    
    def _parse_function_declaration(self, tokens: List[Token], start: int, file_path: Optional[str] = None) -> Tuple[ASTNode, int]:
        """Parse une déclaration de fonction"""
        node = ASTNode(type=NodeType.FUNCTION_DECLARATION, original_language='javascript')
        i = start + 1  # Skip 'function'
        
        # Nom de la fonction
        if i < len(tokens) and tokens[i].type == 'IDENTIFIER':
            node.set_attribute('name', tokens[i].value)
            i += 1
        
        # Paramètres
        if i < len(tokens) and tokens[i].type == 'LPAREN':
            i += 1
            parameters = []
            while i < len(tokens) and tokens[i].type != 'RPAREN':
                if tokens[i].type == 'IDENTIFIER':
                    parameters.append(tokens[i].value)
                i += 1
            node.set_attribute('parameters', parameters)
            if i < len(tokens) and tokens[i].type == 'RPAREN':
                i += 1
        
        # Corps de la fonction (simplifié)
        if i < len(tokens) and tokens[i].type == 'LBRACE':
            body_start = i
            brace_count = 1
            i += 1
            while i < len(tokens) and brace_count > 0:
                if tokens[i].type == 'LBRACE':
                    brace_count += 1
                elif tokens[i].type == 'RBRACE':
                    brace_count -= 1
                i += 1
            
            # Parse le corps (récursif simplifié)
            body_tokens = tokens[body_start + 1:i - 1]
            body_node = ASTNode(type=NodeType.BLOCK_STATEMENT, original_language='javascript')
            node.add_child(body_node)
        
        self._set_source_range(node, tokens[start], tokens[min(i-1, len(tokens)-1)], file_path)
        return node, i - start
    
    def _parse_variable_declaration(self, tokens: List[Token], start: int, file_path: Optional[str] = None) -> Tuple[ASTNode, int]:
        """Parse une déclaration de variable"""
        node = ASTNode(type=NodeType.VARIABLE_DECLARATION, original_language='javascript')
        node.set_attribute('kind', tokens[start].value)  # const, let, var
        
        i = start + 1
        
        # Nom de la variable
        if i < len(tokens) and tokens[i].type == 'IDENTIFIER':
            node.set_attribute('name', tokens[i].value)
            i += 1
        
        # Valeur d'initialisation
        if i < len(tokens) and tokens[i].type == 'ASSIGN':
            i += 1
            # Parse la valeur (simplifié)
            if i < len(tokens):
                value_node = self._parse_expression(tokens, i, file_path)
                if value_node:
                    node.add_child(value_node[0])
                    i += value_node[1]
        
        # Skip semicolon
        if i < len(tokens) and tokens[i].type == 'SEMICOLON':
            i += 1
        
        self._set_source_range(node, tokens[start], tokens[min(i-1, len(tokens)-1)], file_path)
        return node, i - start
    
    def _parse_expression(self, tokens: List[Token], start: int, file_path: Optional[str] = None) -> Tuple[Optional[ASTNode], int]:
        """Parse une expression simple"""
        if start >= len(tokens):
            return None, 0
        
        token = tokens[start]
        
        # Littéraux
        if token.type in ['STRING_DOUBLE', 'STRING_SINGLE', 'STRING_TEMPLATE']:
            node = ASTNode(type=NodeType.LITERAL, original_language='javascript')
            node.set_attribute('value', token.value[1:-1])  # Remove quotes
            node.set_attribute('data_type', DataType.STRING.value)
            self._set_source_range(node, token, token, file_path)
            return node, 1
        
        elif token.type == 'NUMBER':
            node = ASTNode(type=NodeType.LITERAL, original_language='javascript')
            value = float(token.value) if '.' in token.value else int(token.value)
            node.set_attribute('value', value)
            node.set_attribute('data_type', DataType.FLOAT.value if '.' in token.value else DataType.INTEGER.value)
            self._set_source_range(node, token, token, file_path)
            return node, 1
        
        elif token.type in ['TRUE', 'FALSE']:
            node = ASTNode(type=NodeType.LITERAL, original_language='javascript')
            node.set_attribute('value', token.value == 'true')
            node.set_attribute('data_type', DataType.BOOLEAN.value)
            self._set_source_range(node, token, token, file_path)
            return node, 1
        
        elif token.type == 'NULL':
            node = ASTNode(type=NodeType.LITERAL, original_language='javascript')
            node.set_attribute('value', None)
            node.set_attribute('data_type', DataType.NULL.value)
            self._set_source_range(node, token, token, file_path)
            return node, 1
        
        elif token.type == 'UNDEFINED':
            node = ASTNode(type=NodeType.LITERAL, original_language='javascript')
            node.set_attribute('value', None)
            node.set_attribute('data_type', DataType.UNDEFINED.value)
            self._set_source_range(node, token, token, file_path)
            return node, 1
        
        # Identifiants
        elif token.type == 'IDENTIFIER':
            node = ASTNode(type=NodeType.IDENTIFIER, original_language='javascript')
            node.set_attribute('name', token.value)
            self._set_source_range(node, token, token, file_path)
            return node, 1
        
        return None, 1
    
    def _parse_if_statement(self, tokens: List[Token], start: int, file_path: Optional[str] = None) -> Tuple[ASTNode, int]:
        """Parse une instruction if (simplifié)"""
        node = ASTNode(type=NodeType.IF_STATEMENT, original_language='javascript')
        i = start + 1  # Skip 'if'
        
        # Skip jusqu'à la fin de l'instruction (simplifié)
        while i < len(tokens) and tokens[i].type != 'RBRACE':
            i += 1
        if i < len(tokens):
            i += 1
        
        self._set_source_range(node, tokens[start], tokens[min(i-1, len(tokens)-1)], file_path)
        return node, i - start
    
    def _parse_for_statement(self, tokens: List[Token], start: int, file_path: Optional[str] = None) -> Tuple[ASTNode, int]:
        """Parse une boucle for (simplifié)"""
        node = ASTNode(type=NodeType.FOR_STATEMENT, original_language='javascript')
        i = start + 1
        
        # Skip jusqu'à la fin de la boucle (simplifié)
        while i < len(tokens) and tokens[i].type != 'RBRACE':
            i += 1
        if i < len(tokens):
            i += 1
        
        self._set_source_range(node, tokens[start], tokens[min(i-1, len(tokens)-1)], file_path)
        return node, i - start
    
    def _parse_while_statement(self, tokens: List[Token], start: int, file_path: Optional[str] = None) -> Tuple[ASTNode, int]:
        """Parse une boucle while (simplifié)"""
        node = ASTNode(type=NodeType.WHILE_STATEMENT, original_language='javascript')
        i = start + 1
        
        # Skip jusqu'à la fin de la boucle (simplifié)
        while i < len(tokens) and tokens[i].type != 'RBRACE':
            i += 1
        if i < len(tokens):
            i += 1
        
        self._set_source_range(node, tokens[start], tokens[min(i-1, len(tokens)-1)], file_path)
        return node, i - start
    
    def _parse_return_statement(self, tokens: List[Token], start: int, file_path: Optional[str] = None) -> Tuple[ASTNode, int]:
        """Parse une instruction return"""
        node = ASTNode(type=NodeType.RETURN_STATEMENT, original_language='javascript')
        i = start + 1
        
        # Parse la valeur de retour si présente
        if i < len(tokens) and tokens[i].type != 'SEMICOLON':
            expr, consumed = self._parse_expression(tokens, i, file_path)
            if expr:
                node.add_child(expr)
                i += consumed
        
        # Skip semicolon
        if i < len(tokens) and tokens[i].type == 'SEMICOLON':
            i += 1
        
        self._set_source_range(node, tokens[start], tokens[min(i-1, len(tokens)-1)], file_path)
        return node, i - start
    
    def _parse_break_statement(self, tokens: List[Token], start: int, file_path: Optional[str] = None) -> Tuple[ASTNode, int]:
        """Parse une instruction break"""
        node = ASTNode(type=NodeType.BREAK_STATEMENT, original_language='javascript')
        i = start + 1
        
        if i < len(tokens) and tokens[i].type == 'SEMICOLON':
            i += 1
        
        self._set_source_range(node, tokens[start], tokens[min(i-1, len(tokens)-1)], file_path)
        return node, i - start
    
    def _parse_continue_statement(self, tokens: List[Token], start: int, file_path: Optional[str] = None) -> Tuple[ASTNode, int]:
        """Parse une instruction continue"""
        node = ASTNode(type=NodeType.CONTINUE_STATEMENT, original_language='javascript')
        i = start + 1
        
        if i < len(tokens) and tokens[i].type == 'SEMICOLON':
            i += 1
        
        self._set_source_range(node, tokens[start], tokens[min(i-1, len(tokens)-1)], file_path)
        return node, i - start
    
    def _parse_class_declaration(self, tokens: List[Token], start: int, file_path: Optional[str] = None) -> Tuple[ASTNode, int]:
        """Parse une déclaration de classe (simplifié)"""
        node = ASTNode(type=NodeType.CLASS_DECLARATION, original_language='javascript')
        i = start + 1
        
        # Nom de la classe
        if i < len(tokens) and tokens[i].type == 'IDENTIFIER':
            node.set_attribute('name', tokens[i].value)
            i += 1
        
        # Skip jusqu'à la fin de la classe (simplifié)
        while i < len(tokens) and tokens[i].type != 'RBRACE':
            i += 1
        if i < len(tokens):
            i += 1
        
        self._set_source_range(node, tokens[start], tokens[min(i-1, len(tokens)-1)], file_path)
        return node, i - start
    
    def _parse_import_export(self, tokens: List[Token], start: int, file_path: Optional[str] = None) -> Tuple[ASTNode, int]:
        """Parse une instruction import/export (simplifié)"""
        node = ASTNode(type=NodeType.IMPORT_DECLARATION, original_language='javascript')
        node.set_attribute('type', tokens[start].value)  # import ou export
        i = start + 1
        
        # Skip jusqu'au semicolon ou fin de ligne
        while i < len(tokens) and tokens[i].type != 'SEMICOLON':
            i += 1
        if i < len(tokens):
            i += 1
        
        self._set_source_range(node, tokens[start], tokens[min(i-1, len(tokens)-1)], file_path)
        return node, i - start
    
    def _parse_expression_statement(self, tokens: List[Token], start: int, file_path: Optional[str] = None) -> Tuple[ASTNode, int]:
        """Parse une instruction d'expression"""
        expr, consumed = self._parse_expression(tokens, start, file_path)
        if expr:
            stmt = ASTNode(type=NodeType.EXPRESSION_STATEMENT, original_language='javascript')
            stmt.add_child(expr)
            return stmt, consumed
        return None, 1
    
    def _set_source_range(self, node: ASTNode, start_token: Token, end_token: Token, file_path: Optional[str] = None) -> None:
        """Définit la plage source d'un nœud"""
        node.source_range = SourceRange(
            start=SourceLocation(start_token.line, start_token.column, file_path),
            end=SourceLocation(end_token.line, end_token.column + len(end_token.value), file_path)
        )

