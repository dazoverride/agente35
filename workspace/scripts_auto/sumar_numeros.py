# DESCRIPCION: Suma todos los números proporcionados como argumentos en la línea de comandos. Uso: python sumar_numeros.py num1 num2 num3 ...
import sys

def main():
    if len(sys.argv) < 2:
        print("Uso: python sumar_numeros.py num1 num2 num3...")
        return
    
    try:
        numeros = [int(arg) for arg in sys.argv[1:]]
        suma = sum(numeros)
        print(suma)
    except ValueError:
        print("Error: Por favor, proporciona solo números enteros como argumentos.")

if __name__ == "__main__":
    main()
