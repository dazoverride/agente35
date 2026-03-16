# Cifrador de Mensajes AES-256

Un script interactivo para cifrar y descifrar mensajes utilizando el estándar de cifrado simétrico AES-256. Utiliza derivación de claves mediante PBKDF2 para mayor seguridad.

## Características
- Cifrado AES en modo CBC (Cipher Block Chaining).
- Derivación de claves segura usando PBKDF2 con SHA-256.
- Relleno PKCS7 para bloques de datos.
- Almacenamiento seguro de la 'salt' y 'IV' en archivos JSON separados del mensaje cifrado.

## Instalación
```bash
pip install pycryptodome
```

## Uso

### Cifrar un mensaje:
```bash
python 29_cifrador_mensajes_aes.py --cipher --password "mi_clave_segura" --mensaje "Este es un secreto" --save-key --key-file "mi_clave.json"
```

### Descifrar un mensaje:
```bash
python 29_cifrador_mensajes_aes.py --decrypt --password "mi_clave_segura" --archivo_cifrado "datos_cifrados.json"
```

### Guardar solo la clave (inicialización):
```bash
python 29_cifrador_mensajes_aes.py --save-key --password "mi_clave_segura" --key-file "mi_clave.json"
```

## Estructura de Datos
Los datos cifrados se guardan en un diccionario JSON con las siguientes claves:
- `salt`: Sal utilizada para derivar la clave (base64).
- `iv`: Vector de inicialización (base64).
- `ciphertext`: Texto cifrado (base64).

## Advertencias
- Mantén tu contraseña segura. Si la pierdes, no podrás descifrar los datos.
- Este script no es apto para criptografía de grado militar o financiero.
