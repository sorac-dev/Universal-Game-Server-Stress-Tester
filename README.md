# Universal Game Server Stress Tester v2

> **Solo para entornos de laboratorio controlados.**

## Descripción

Este proyecto proporciona un **stress tester universal** capaz de generar ataques de saturación (flooding) a servidores de juego. Soporta múltiples protocolos y modos:

- **UDP Flood genérico**
- **TCP Flood genérico**
- **UDP‑spoof** (IP falsificadas, solo en Linux con permisos root)
- **Handshake spam** para **SAMP/MTA**
- **Handshake + Status spam** para **Minecraft**
- **Modo combo**: lanza varios ataques simultáneamente

El objetivo es poner a prueba la resistencia de servidores en un **laboratorio de ciberseguridad**, no para usos malintencionados en producción.

---

## Tabla de Contenidos

1. [Características](#caracter%C3%ADsticas)
2. [Requisitos](#requisitos)
3. [Instalación](#instalaci%C3%B3n)
4. [Uso](#uso)
5. [Modos de Ataque](#modos-de-ataque)
6. [Configuración Avanzada](#configuraci%C3%B3n-avanzada)
7. [Ejemplos](#ejemplos)
8. [Disclaimer](#disclaimer)
9. [Licencia](#licencia)

---

## Características

- **Multiplataforma** (Windows/macOS/Linux) para modos estándar
- **Multiprocessing + asyncio** para máxima eficiencia
- **Multithreading** dentro de cada proceso
- **CLI limpia** con `argparse`
- **Jitter** y **paquetes variables** para evadir filtros
- **Estadísticas en vivo** (paquetes/s, uso de CPU)

## Requisitos

- Python 3.8 o superior
- Paquetes: estándar de la librería Python (`argparse`, `asyncio`, `multiprocessing`, `psutil`, etc.)
- **Linux** y **privilegios root** para modo `udp‑spoof`

## Instalación

1. Clona el repositorio:
   ```bash
   git clone https://github.com/tu_usuario/universal-stress-tester.git
   cd universal-stress-tester
   ```
2. (Opcional) Crea un entorno virtual:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Instala dependencias:
   ```bash
   pip install psutil
   ```

## Uso

Ejecuta el script con la forma básica:

```bash
python3 stress_tester.py <modo> <host> [opciones]
```

Mostrará confirmación antes de iniciar. Ejemplo:

```bash
python3 stress_tester.py udp 192.168.1.50 -p 7777 -d 60 --min-pkt 512 --max-pkt 1024 -c 200 -P 4
```

## Modos de Ataque

| Modo       | Descripción                                          |
|------------|------------------------------------------------------|
| `udp`      | Flood UDP genérico                                   |
| `tcp`      | Flood TCP genérico                                   |
| `udp-spoof`| Flood UDP con IP spoofing (raw sockets, Linux)       |
| `samp`     | Handshake spam para SAMP/MTA                         |
| `mc`       | Handshake + Status spam para Minecraft               |
| `combo`    | Ejecuta varios modos en paralelo (udp, tcp, samp, mc)|

## Configuración Avanzada

- `--delay`: Tiempo base entre envíos (segundos)
- `--jitter`: Variación aleatoria en delay para evadir detección
- `--min-pkt`, `--max-pkt`: Tamaño mínimo y máximo de paquete
- `--concurrency`: Hilos por proceso (por defecto: `cpu_count() * 50`)
- `--processes`: Número de procesos a lanzar (por defecto: núcleos CPU)

## Ejemplos

1. **UDP Flood** durante 30 s con paquetes de 1 KB:
   ```bash
   python3 stress_tester.py udp 10.0.0.5 -p 7777 -d 30 --min-pkt 1024 --max-pkt 1024
   ```

2. **Combo** en servidor Minecraft y SAMP:
   ```bash
   python3 stress_tester.py combo example.com -d 45 --delay 0.02 -c 100 -P 2
   ```

## Disclaimer

**Uso exclusivo en laboratorios de pruebas controladas y con autorización expresa**. Cualquier uso no autorizado es ilegal y está penado por la ley.

## Licencia

Este proyecto está licenciado bajo **MIT License**. Consulta el archivo `LICENSE` para más detalles.

