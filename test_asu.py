#!/usr/bin/env python3
"""
Script de test pour l'Arbre Syntaxique Universel de Léa
Teste les parsers Python et JavaScript avec des exemples de code.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from src.parsers.python_parser import PythonParser
from src.parsers.javascript_parser import JavaScriptParser
from src.parsers.base_parser import parser_registry, parse_code
import json


def test_python_parser():
    """Test du parser Python"""
    print("=== Test du Parser Python ===")
    
    python_code = '''
def fibonacci(n):
    """Calcule le n-ième nombre de Fibonacci"""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

class Calculator:
    def __init__(self):
        self.result = 0
    
    def add(self, x, y):
        self.result = x + y
        return self.result

# Test
calc = Calculator()
result = calc.add(5, 3)
print(f"Résultat: {result}")

for i in range(5):
    print(f"Fibonacci({i}) = {fibonacci(i)}")
'''
    
    try:
        parser = PythonParser()
        ust = parser.parse(python_code, "test.py")
        
        print(f"✓ Parsing réussi!")
        print(f"  - Langage: {ust.metadata['language']}")
        print(f"  - Nœuds racine: {len(ust.root.children)}")
        
        # Analyse des fonctions
        from src.models.ast_universal import NodeType
        functions = ust.get_nodes_by_type(NodeType.FUNCTION_DECLARATION)
        print(f"  - Fonctions trouvées: {len(functions)}")
        for func in functions:
            name = func.get_attribute('name', 'anonymous')
            params = func.get_attribute('parameters', [])
            print(f"    * {name}({', '.join(params)})")
        
        # Analyse des classes
        classes = ust.get_nodes_by_type(NodeType.CLASS_DECLARATION)
        print(f"  - Classes trouvées: {len(classes)}")
        for cls in classes:
            name = cls.get_attribute('name', 'unknown')
            print(f"    * {name}")
        
        print(f"  - JSON ASU (premiers 200 caractères):")
        json_str = ust.to_json()
        print(f"    {json_str[:200]}...")
        
    except Exception as e:
        print(f"✗ Erreur: {e}")
        import traceback
        traceback.print_exc()


def test_javascript_parser():
    """Test du parser JavaScript"""
    print("\n=== Test du Parser JavaScript ===")
    
    js_code = '''
function calculateArea(radius) {
    const pi = 3.14159;
    return pi * radius * radius;
}

class Circle {
    constructor(radius) {
        this.radius = radius;
    }
    
    getArea() {
        return calculateArea(this.radius);
    }
}

const circle = new Circle(5);
const area = circle.getArea();
console.log(`Area: ${area}`);

for (let i = 0; i < 3; i++) {
    console.log(`Circle ${i}: ${calculateArea(i + 1)}`);
}

if (area > 50) {
    console.log("Large circle");
} else {
    console.log("Small circle");
}
'''
    
    try:
        parser = JavaScriptParser()
        ust = parser.parse(js_code, "test.js")
        
        print(f"✓ Parsing réussi!")
        print(f"  - Langage: {ust.metadata['language']}")
        print(f"  - Nœuds racine: {len(ust.root.children)}")
        
        # Analyse des fonctions
        from src.models.ast_universal import NodeType
        functions = ust.get_nodes_by_type(NodeType.FUNCTION_DECLARATION)
        print(f"  - Fonctions trouvées: {len(functions)}")
        for func in functions:
            name = func.get_attribute('name', 'anonymous')
            params = func.get_attribute('parameters', [])
            print(f"    * {name}({', '.join(params)})")
        
        # Analyse des variables
        variables = ust.get_nodes_by_type(NodeType.VARIABLE_DECLARATION)
        print(f"  - Variables trouvées: {len(variables)}")
        for var in variables:
            name = var.get_attribute('name', 'unknown')
            kind = var.get_attribute('kind', 'var')
            print(f"    * {kind} {name}")
        
        # Analyse des classes
        classes = ust.get_nodes_by_type(NodeType.CLASS_DECLARATION)
        print(f"  - Classes trouvées: {len(classes)}")
        for cls in classes:
            name = cls.get_attribute('name', 'unknown')
            print(f"    * {name}")
        
    except Exception as e:
        print(f"✗ Erreur: {e}")
        import traceback
        traceback.print_exc()


def test_registry():
    """Test du registre des parsers"""
    print("\n=== Test du Registre des Parsers ===")
    
    # Enregistrement des parsers
    parser_registry.register_parser(PythonParser())
    parser_registry.register_parser(JavaScriptParser())
    
    print(f"✓ Langages supportés: {parser_registry.list_supported_languages()}")
    print(f"✓ Extensions supportées: {parser_registry.list_supported_extensions()}")
    
    # Test de détection automatique
    test_codes = [
        ("def hello(): pass", "python"),
        ("function hello() {}", "javascript"),
        ("class Test: pass", "python"),
        ("const x = 5;", "javascript")
    ]
    
    for code, expected in test_codes:
        try:
            # Utilise la détection automatique
            from src.parsers.base_parser import detect_language
            detected_lang = detect_language(code)
            if detected_lang:
                ust = parse_code(code, detected_lang)
                detected = ust.metadata['language']
                status = "✓" if detected == expected else "✗"
                print(f"  {status} '{code[:20]}...' -> {detected} (attendu: {expected})")
            else:
                print(f"  ✗ '{code[:20]}...' -> Langage non détecté")
        except Exception as e:
            print(f"  ✗ '{code[:20]}...' -> Erreur: {e}")


def test_conversion_json():
    """Test de la sérialisation/désérialisation JSON"""
    print("\n=== Test de Conversion JSON ===")
    
    python_code = "def test(x): return x * 2"
    
    try:
        parser = PythonParser()
        ust1 = parser.parse(python_code)
        
        # Sérialisation
        json_str = ust1.to_json()
        print(f"✓ Sérialisation JSON réussie ({len(json_str)} caractères)")
        
        # Désérialisation
        from src.models.ast_universal import UniversalSyntaxTree
        ust2 = UniversalSyntaxTree.from_json(json_str)
        print(f"✓ Désérialisation JSON réussie")
        
        # Vérification
        assert ust1.metadata['language'] == ust2.metadata['language']
        assert ust1.root.type == ust2.root.type
        assert len(ust1.root.children) == len(ust2.root.children)
        print(f"✓ Vérification de cohérence réussie")
        
    except Exception as e:
        print(f"✗ Erreur: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("🚀 Tests de l'Arbre Syntaxique Universel de Léa")
    print("=" * 50)
    
    test_python_parser()
    test_javascript_parser()
    test_registry()
    test_conversion_json()
    
    print("\n" + "=" * 50)
    print("✅ Tests terminés!")

