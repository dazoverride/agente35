import subprocess
import time
import sys
from datetime import datetime

def run_command(cmd, timeout=10):
    try:
        proc = subprocess.Popen(
            cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        stdout, stderr = proc.communicate(timeout=timeout)
        return proc.returncode, stdout, stderr
    except subprocess.TimeoutExpired:
        proc.kill()
        stdout, stderr = proc.communicate()
        return -1, stdout, f"Timeout: {stderr}"

def check_service_status(service_name):
    result = run_command(f"systemctl is-active {service_name}")
    if result[0] == 0:
        return "active"
    else:
        return "inactive"

def get_service_logs(service_name, lines=10):
    result = run_command(f"journalctl -u {service_name} -n {lines}")
    if result[1]:
        return result[1].strip()
    return ""

def main():
    print("=== Monitor de Servicios Sistem ===")
    print(f"Fecha/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 40)
    
    services = ["nginx", "mysql", "redis", "docker", "postgresql", "ssh"]
    
    for svc in services:
        status = check_service_status(svc)
        logs = get_service_logs(svc, 3)
        
        if status == "active":
            print(f"[OK] {svc:12} | Estado: {status}")
        else:
            print(f"[!] {svc:12} | Estado: {status}")
            if logs:
                print(f"      Últimos logs:")
                for line in logs.split('\n'):
                    if line:
                        print(f"        - {line}")
        print()

if __name__ == "__main__":
    main()
