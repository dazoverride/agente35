import json
import os
import hashlib
from datetime import datetime
from pathlib import Path
import shutil

# Configuración básica
BASE_DIR = Path('.')
CONFIG_FILE = BASE_DIR / 'config_sincronizacion.json'
LOG_FILE = BASE_DIR / 'logs_sincronizacion.json'

# Cargar configuración o inicializar
config = {}
if CONFIG_FILE.exists():
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
else:
    config = {
        'local_folder': str(BASE_DIR / 'datos_locale'),
        'remote_folder': 'https://ejemplo.com/backup', # Simulado, requiere librería como google-cloud-storage o ftp
        'auto_sync': False
    }
    save_config()

def save_config():
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

def get_file_hash(filepath):
    """Calcula hash MD5 de un archivo para detectar cambios."""
    hash_md5 = hashlib.md5()
    try:
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                hash_md5.update(byte_block)
        return hash_md5.hexdigest()
    except Exception:
        return None

def sync_file(local_path, remote_path, config):
    """Sincroniza un archivo local con remoto (simulación lógica)."""
    if not os.path.exists(local_path):
        print(f"Archivo no encontrado: {local_path}")
        return False
    
    local_hash = get_file_hash(local_path)
    if not local_hash:
        return False
    
    # Simulación de estado remoto (en producción, esto vendría de un servidor o API)
    remote_exists = False
    remote_hash = None
    
    # Simulamos que el archivo remoto existe con un hash diferente para probar subida
    if os.path.basename(local_path) == 'archivo_nuevo.txt':
        remote_exists = False
    elif os.path.basename(local_path) == 'archivo_modificado.txt':
        remote_exists = True
        remote_hash = 'old_hash_123'
    else:
        remote_exists = True
        remote_hash = local_hash # Si es igual, no hace nada
    
    if not remote_exists:
        print(f"Subiendo nuevo archivo: {local_path}")
        # Aquí iría la lógica real de subida a cloud
        log_action('UPLOAD', local_path, datetime.now().isoformat())
        return True
    elif remote_hash != local_hash:
        print(f"Sincronizando cambios en: {local_path}")
        # Aquí iría la lógica real de actualización
        log_action('UPDATE', local_path, datetime.now().isoformat())
        return True
    else:
        print(f"Archivo {local_path} está actualizado.")
        return False

def log_action(action_type, file_path, timestamp):
    """Registra la acción en el log de sincronización."""
    log_entry = {
        'timestamp': timestamp,
        'action': action_type,
        'file': file_path
    }
    
    if LOG_FILE.exists():
        with open(LOG_FILE, 'r') as f:
            logs = json.load(f)
    else:
        logs = []
    
    logs.append(log_entry)
    
    # Mantener solo los últimos 100 registros para no saturar disco
    if len(logs) > 100:
        logs = logs[-100:]
    
    with open(LOG_FILE, 'w') as f:
        json.dump(logs, f, indent=4)

def scan_and_sync_folder(local_folder, config):
    """Escanea la carpeta local y sincroniza archivos nuevos o modificados."""
    synced_count = 0
    skipped_count = 0
    
    local_path = Path(local_folder)
    if not local_path.exists():
        print(f"Carpeta local no existe: {local_folder}")
        return 0, 0
    
    for file_path in local_path.iterdir():
        if file_path.is_file():
            # Ignorar archivos de sistema y logs de la propia herramienta
            if file_path.name.startswith('.') or file_path.name in ['config_sincronizacion.json', 'logs_sincronizacion.json']:
                continue
            
            success = sync_file(str(file_path), config['remote_folder'], config)
            if success:
                synced_count += 1
            else:
                skipped_count += 1
    
    return synced_count, skipped_count

def main():
    print("=== Automatizador de Sincronización Cloud ===")
    print(f"Carpeta Local: {config['local_folder']}")
    print("Iniciando escaneo...")
    
    synced, skipped = scan_and_sync_folder(config['local_folder'], config)
    
    print(f"\nResumen:")
    print(f"Archivos sincronizados: {synced}")
    print(f"Archivos ya actualizados/skipped: {skipped}")
    print("Sincronización completada.")

if __name__ == "__main__":
    main()
