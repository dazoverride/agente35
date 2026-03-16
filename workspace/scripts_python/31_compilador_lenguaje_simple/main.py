import json
import sys
import os
from typing import List, Tuple, Dict

class SimpleCompiler:
    """Compilador simple para un lenguaje de dominio específico (DSL) basado en tokens."""
    
    def __init__(self):
        self.variables: Dict[str, any] = {}
        self.functions: Dict[str, List] = {}
        self.errors: List[str] = []
        self.output: List[str] = []
        
    def tokenize(self, code: str) -> List[Tuple[str, str]]:
        """Tokeniza el código fuente básico."""
        tokens = []
        keywords = {'var', 'func', 'print', 'if', 'else', 'return', 'import'}
        
        i = 0
        while i < len(code):
            if code[i].isspace():
                i += 1
                continue
            
            if code[i].isdigit() or code[i] == '.':
                num = ''
                while i < len(code) and (code[i].isdigit() or code[i] == '.'):
                    num += code[i]
                    i += 1
                tokens.append(('NUMBER', num))
                continue
            
            if code[i].isalpha() or code[i] == '_':
                word = ''
                while i < len(code) and (code[i].isalnum() or code[i] == '_'):
                    word += code[i]
                    i += 1
                if word in keywords:
                    tokens.append(('KEYWORD', word))
                else:
                    tokens.append(('IDENT', word))
                continue
            
            if code[i] in '+-*/=(){}[];':
                tokens.append(('OP', code[i]))
                i += 1
                continue
            
            raise SyntaxError(f"Carácter inválido: {code[i]}")
        
        return tokens

    def parse_and_execute(self, code: str) -> None:
        """Parsa y ejecuta el código tokenizado."""
        try:
            tokens = self.tokenize(code)
            self.errors = []
            self.output = []
            self.variables = {}
            self.functions = {}
            
            # Simulación de ejecución de instrucciones básicas
            # En un compilador real, aquí iría un parser recursivo descendente
            
            i = 0
            while i < len(tokens):
                token_type, value = tokens[i]
                
                if token_type == 'KEYWORD' and value == 'var':
                    i += 1
                    if i < len(tokens) and tokens[i][0] == 'IDENT':
                        var_name = tokens[i][1]
                        i += 1
                        if i < len(tokens) and tokens[i][0] == 'NUMBER':
                            self.variables[var_name] = int(tokens[i][1])
                            i += 1
                        elif i < len(tokens) and tokens[i][0] == 'IDENT':
                            # Asignar valor de otra variable
                            self.variables[var_name] = self.variables.get(tokens[i][1], 0)
                            i += 1
                        else:
                            self.errors.append(f"Error en declaración de variable: {var_name}")
                    else:
                        self.errors.append("Nombre de variable faltante")
                        i += 1
                
                elif token_type == 'KEYWORD' and value == 'print':
                    i += 1
                    if i < len(tokens) and tokens[i][0] == 'IDENT':
                        var_name = tokens[i][1]
                        self.output.append(str(self.variables.get(var_name, 'None')))
                        i += 1
                    elif i < len(tokens) and tokens[i][0] == 'NUMBER':
                        self.output.append(tokens[i][1])
                        i += 1
                
                elif token_type == 'KEYWORD' and value == 'func':
                    i += 1
                    if i < len(tokens) and tokens[i][0] == 'IDENT':
                        func_name = tokens[i][1]
                        i += 1
                        # Simplificación: no se procesa el cuerpo de la función en este ejemplo básico
                        self.functions[func_name] = []
                        self.output.append(f"Función '{func_name}' definida (cuerpo ignorado para demo)")
                        i += 1
                
                elif token_type == 'KEYWORD' and value == 'import':
                    i += 1
                    if i < len(tokens) and tokens[i][0] == 'IDENT':
                        module = tokens[i][1]
                        self.output.append(f"Módulo '{module}' importado (simulado)")
                        i += 1
                
                else:
                    self.errors.append(f"Token no reconocido o sintaxis inválida en posición {i}: {token_type} '{value}'")
                    i += 1
                
        except Exception as e:
            self.errors.append(str(e))

    def run(self, code: str) -> Tuple[List[str], List[str]]:
        """Ejecuta el código y devuelve salida y errores."""
        self.parse_and_execute(code)
        return self.output, self.errors

def main():
    # Script de prueba (DSL simple)
    test_code = '''
var salud = 100;
var nombre = "Usuario";
func saludar() { print("Hola", salud); }
print "Bienvenido", nombre;
import math;
var resultado = salud + 50;
print resultado;
'''
    
    print("=== Compilador Simple Python (DSL) ===")
    print("Analizando código...\n")
    
    compiler = SimpleCompiler()
    output, errors = compiler.run(test_code)
    
    if errors:
        print("--- ERRORES ---")
        for err in errors:
            print(err)
    
    if output:
        print("--- SALIDA ---")
        for line in output:
            print(line)

if __name__ == "__main__":
    main()
