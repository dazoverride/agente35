# Automatizador de Envío de Correos (Email Scheduler)

## Descripción
Este script automatiza el proceso de envío de notificaciones por correo electrónico. Es ideal para sistemas que requieren enviar reportes diarios, alertas de estado o notificaciones masivas a una lista de clientes.

## Características
- Envío masivo a múltiples destinatarios definidos.
- Plantillas de correo dinámicas con datos personalizados.
- Manejo de errores para cada intento de envío.
- Configuración modular de credenciales SMTP.

## Requisitos
- Python 3.6+
- Acceso a un servidor SMTP (ej. Gmail, Outlook, etc.)
- Permisos de administrador para configurar variables de entorno (opcional)

## Cómo ejecutarlo
1. Edita la sección `SMTP_CONFIG` en el archivo `main.py` con tus credenciales reales.
2. Añade o modifica los destinatarios en la lista `DESTINATARIOS`.
3. Ejecuta el script:
   ```bash
   python main.py
   ```

## Advertencia de Seguridad
Nunca compartas tus contraseñas de aplicación SMTP en repositorios públicos. Usa variables de entorno (`os.environ`) para almacenar credenciales en producción.

## Autor
Arquitectura de Fábrica de Software Python Autónoma