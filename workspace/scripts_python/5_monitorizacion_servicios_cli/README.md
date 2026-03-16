# Monitor de Servicios CLI

Un script en Python para monitorear el estado de servicios comunes del sistema (como Nginx, MySQL, Docker, etc.) y mostrar sus últimos registros de error o actividad.

## Requisitos
- Python 3.x
- Permisos de root/sudo para verificar servicios y logs (recomendado)

## Uso
Ejecuta el script directamente:
```bash
python 5_monitorizacion_servicios_cli.py
```

O con permisos de administrador:
```bash
sudo python 5_monitorizacion_servicios_cli.py
```

## Funcionalidades
- Verifica el estado activo/inactivo de servicios comunes.
- Muestra los últimos 3 registros (logs) de cada servicio.
- Salida formateada en consola para fácil lectura.

## Servicios Monitorizados por defecto
- nginx
- mysql
- redis
- docker
- postgresql
- ssh

> Nota: Los nombres de los servicios pueden variar según la distribución Linux o configuración del sistema.