import json
import random
import time
import threading
from datetime import datetime

class SimuladorCiberataque:
    def __init__(self, num_servidores=10):
        self.num_servidores = num_servidores
        self.servidores = [f"srv-{i}" for i in range(num_servidores)]
        self.ataques = []
        self.logs = []
        self.status_servidores = {srv: "activo" for srv in self.servidores}

    def generar_ip(self):
        return f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}"

    def lanzar_ataque_ddos(self, tipo="syn", intensidad=100):
        victimas = random.sample(self.servidores, k=random.randint(1, len(self.servidores)))
        origen = self.generar_ip()
        inicio = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        ataque = {
            "id": len(self.ataques) + 1,
            "tipo": tipo,
            "origen": origen,
            "victimas": victimas,
            "intensidad": intensidad,
            "inicio": inicio
        }
        self.ataques.append(ataque)
        self.logs.append(f"[{inicio}] ATACA {tipo.upper()} desde {origen} a {', '.join(victimas)} (Intensidad: {intensidad})")
        return ataque

    def simular_defensa(self):
        bloqueados = random.sample(self.ataques, k=min(3, len(self.ataques)))
        for ataque in bloqueados:
            self.logs.append(f"[Defensa] Bloqueado ataque #{ataque['id']} desde {ataque['origen']}")
        return len(bloqueados)

    def reportar(self):
        print("=" * 60)
        print(f"\nREPORTE DE SIMULACIÓN - {datetime.now()}")
        print("=" * 60)
        print(f"Total de Ataques: {len(self.ataques)}")
        print(f"Ataques Bloqueados: {self.simular_defensa()}")
        print("-" * 60)
        print("LOGS DE EVENTOS:")
        for log in self.logs[-10:]:  # Mostrar últimos 10 logs
            print(f"  {log}")
        print("=" * 60)

    def ejecutar_simulacion(self, duracion=5):
        print("Iniciando simulación de red...\n")
        for _ in range(duracion):
            if random.random() > 0.7:  # 30% probabilidad de ataque por turno
                self.lanzar_ataque_ddos(tipo=random.choice(["syn", "udp", "amp"]), intensidad=random.randint(50, 200))
            time.sleep(1)
        self.reportar()

if __name__ == "__main__":
    sim = SimuladorCiberataque(num_servidores=8)
    sim.ejecutar_simulacion(duracion=10)
