#!/usr/bin/env python3
"""
Automatizador de envío de correos electrónicos con reportes programados.
Permite agendar envíos masivos de notificaciones personalizadas basadas en archivos de entrada.
"""

import os
import json
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Dict, Optional

# Configuración de SMTP (Dejar en blanco para usar variables de entorno o editar manualmente)
SMTP_CONFIG = {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "username": "tu_usuario@gmail.com",
    "password": "tu_contraseña_app",
    "sender_email": "tu_usuario@gmail.com"
}

# Lista de destinatarios con plantillas de correo
DESTINATARIOS = [
    {"email": "cliente1@ejemplo.com", "nombre": "Cliente Uno", "asunto": "Reporte Diario"},
    {"email": "cliente2@ejemplo.com", "nombre": "Cliente Dos", "asunto": "Estado del Servicio"},
    {"email": "cliente3@ejemplo.com", "nombre": "Cliente Tres", "asunto": "Notificación de Actualización"}
]

# Función para generar el cuerpo del correo dinámicamente
def generar_cuerpo_correo(destinatario: Dict, id_reporte: int) -> str:
    return f"""
    Estimado/a {destinatario['nombre']},
    
    Le informamos que se ha generado el reporte de ID: {id_reporte}.
    Este es un sistema automatizado de notificación.
    
    Fecha de envío: {datetime.now().strftime("%d/%m/%Y %H:%M")}
    
    Atentamente,
    El Sistema de Automatización
    """.strip()

# Función para enviar un solo correo
def enviar_correo(destinatario: Dict, asunto: str, cuerpo: str, id_reporte: int) -> bool:
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_CONFIG['sender_email']
        msg['To'] = destinatario['email']
        msg['Subject'] = f"[AUTOMATIZADO] {asunto} - ID: {id_reporte}"
        
        msg.attach(MIMEText(cuerpo, 'plain', 'utf-8'))
        
        with smtplib.SMTP(SMTP_CONFIG['smtp_server'], SMTP_CONFIG['smtp_port']) as server:
            server.starttls()
            server.login(SMTP_CONFIG['username'], SMTP_CONFIG['password'])
            server.send_message(msg)
        
        print(f"[OK] Correo enviado exitosamente a: {destinatario['email']}")
        return True
    except Exception as e:
        print(f"[ERROR] Falló el envío al {destinatario['email']}: {str(e)}")
        return False

# Función principal de orquestación
def main():
    print("="*50)
    print("AUTOMATIZADOR DE EMAILS: INICIANDO PROCESO")
    print("="*50)
    
    # Simulación de generación de ID de reporte único
    id_reporte_actual = int(time.time()) % 1000000
    
    total_destinatarios = len(DESTINATARIOS)
    enviados = 0
    fallidos = 0
    
    for i, destinatario in enumerate(DESTINATARIOS):
        print(f"\nProcesando destinatario {i+1}/{total_destinatarios}...")
        
        cuerpo = generar_cuerpo_correo(destinatario, id_reporte_actual)
        resultado = enviar_correo(destinatario, "Reporte Automático", cuerpo, id_reporte_actual)
        
        if resultado:
            enviados += 1
            time.sleep(1)  # Pausa para evitar bloqueos del servidor SMTP
        else:
            fallidos += 1
    
    print("\n" + "="*50)
    print("RESUMEN DE EJECUCIÓN")
    print(f"Total enviados: {enviados}")
    print(f"Total fallidos: {fallidos}")
    print("Proceso finalizado.")
    print("="*50)

if __name__ == "__main__":
    main()
