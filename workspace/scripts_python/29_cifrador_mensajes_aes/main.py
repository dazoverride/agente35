import argparse
import json
import os
import base64
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2


def generar_clave(password: str, salt: bytes = None) -> tuple:
    """Genera una clave AES-256 derivada de una contraseña usando PBKDF2."""
    if salt is None:
        salt = get_random_bytes(16)
    clave = PBKDF2(password, salt, dkLen=32, count=100000, hmac_hash_module='sha256')
    return clave, salt


def cifrar_mensaje(mensaje: str, clave: bytes, salt: bytes) -> dict:
    """Cifra un mensaje usando AES en modo CBC."""
    iv = get_random_bytes(16)
    cipher = AES.new(clave, AES.MODE_CBC, iv)
    # Relleno PKCS7
    padding_len = 16 - (len(mensaje) % 16)
    mensaje_bytes = mensaje.encode('utf-8') + bytes([padding_len] * padding_len)
    cifrado = cipher.encrypt(mensaje_bytes)
    
    # Estructura JSON: {"salt": base64, "iv": base64, "ciphertext": base64}
    return {
        "salt": base64.b64encode(salt).decode(),
        "iv": base64.b64encode(iv).decode(),
        "ciphertext": base64.b64encode(cifrado).decode()
    }


def descifrar_mensaje(datos_cifrados: dict, password: str) -> str:
    """Descifra un mensaje cifrado."""
    salt = base64.b64decode(datos_cifrados["salt"])
    iv = base64.b64decode(datos_cifrados["iv"])
    ciphertext = base64.b64decode(datos_cifrados["ciphertext"])
    
    clave, _ = generar_clave(password, salt)
    cipher = AES.new(clave, AES.MODE_CBC, iv)
    texto_cifrado = cipher.decrypt(ciphertext)
    
    # Remover padding PKCS7
    padding_len = texto_cifrado[-1]
    texto_plano = texto_cifrado[:-padding_len]
    return texto_plano.decode('utf-8')


def guardar_clave_segura(password: str, salt: bytes, archivo: str):
    """Guarda la clave y el sal en un archivo JSON seguro (sin la contraseña)."""
    datos = {"salt": base64.b64encode(salt).decode()}
    with open(archivo, 'w') as f:
        json.dump(datos, f)


def main():
    parser = argparse.ArgumentParser(description="Cifrador de mensajes AES-256 interactivo.")
    parser.add_argument("--cipher", help="Cifrar un mensaje.")
    parser.add_argument("--decrypt", help="Descifrar un mensaje.")
    parser.add_argument("--save-key", dest="save_key", help="Guardar la clave de cifrado en un archivo.")
    parser.add_argument("--load-key", dest="load_key", help="Cargar la clave de cifrado desde un archivo.")
    parser.add_argument("--key-file", dest="key_file", help="Archivo donde guardar o cargar la clave.")
    parser.add_argument("--password", help="Contraseña para cifrar/descifrar.")
    parser.add_argument("mensaje", help="Mensaje a cifrar (si no se usa --cipher).")
    parser.add_argument("archivo_cifrado", help="Archivo JSON con datos cifrados (si no se usa --decrypt).")

    args = parser.parse_args()

    if not args.password:
        print("Error: Se requiere la opción --password.")
        return

    if args.cipher and args.mensaje:
        # Modo Cifrado
        if args.save_key and args.key_file:
            clave, salt = generar_clave(args.password)
            guardar_clave_segura(args.password, salt, args.key_file)
            print(f"Clave guardada en {args.key_file}")
        else:
            # Generar clave nueva si no se carga
            if args.load_key and args.key_file:
                with open(args.key_file, 'r') as f:
                    datos = json.load(f)
                    salt = base64.b64decode(datos["salt"])
                clave, _ = generar_clave(args.password, salt)
            else:
                clave, salt = generar_clave(args.password)
                guardar_clave_segura(args.password, salt, args.key_file)

        datos = cifrar_mensaje(args.mensaje, clave, salt)
        print(json.dumps(datos, indent=2))

    elif args.decrypt and args.archivo_cifrado:
        # Modo Descifrado
        with open(args.archivo_cifrado, 'r') as f:
            datos = json.load(f)
        mensaje = descifrar_mensaje(datos, args.password)
        print(mensaje)

    elif args.save_key and args.key_file:
        # Solo guardar clave (útil para inicialización)
        clave, salt = generar_clave(args.password)
        guardar_clave_segura(args.password, salt, args.key_file)
        print(f"Clave generada y guardada en {args.key_file}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
