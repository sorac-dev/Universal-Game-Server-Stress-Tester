# 🧪 Universal Game Server Stress Tester v2

> ⚠️ **Este script es solo para entornos de laboratorio controlados y con fines educativos o de pruebas autorizadas.**

## 🧭 Descripción

Este proyecto proporciona un **tester universal de estrés para servidores de juegos**, diseñado para simular distintos tipos de ataques de saturación (flood) con fines de prueba. Soporta múltiples protocolos y modos:

- 🔁 **UDP Flood genérico**
- 🔄 **TCP Flood genérico**
- 🎭 **UDP Spoofing** (IP falsificadas, requiere root y Linux)
- 🎮 **Handshake Spam para SAMP/MTA**
- ⛏️ **Status + Handshake Spam para servidores Minecraft**
- 💥 **Modo Combo**: Ejecuta varios modos de ataque en paralelo

> **Importante:** Este proyecto **no está diseñado para ataques reales** y su uso indebido podría ser ilegal. Úsalo únicamente en entornos de laboratorio.

---

## 📚 Tabla de Contenidos

1. [Características](#-características)
2. [Requisitos](#-requisitos)
3. [Instalación Manual](#-instalación-manual)
4. [Uso](#-uso)
5. [Modos de Ataque](#-modos-de-ataque)
6. [Configuración Avanzada](#-configuración-avanzada)
7. [Ejemplos](#-ejemplos)
8. [Disclaimer](#-disclaimer)
9. [Licencia](#-licencia)

---

## ✅ Características

- ⚙️ Multiplataforma: Windows, macOS y Linux (modo UDP-spoof solo en Linux con root)
- 🚀 Alta eficiencia con `multiprocessing`, `asyncio` y `threading`
- 📊 Estadísticas en tiempo real: paquetes/s y uso de CPU
- 🎯 Paquetes con tamaño variable y delay aleatorio (jitter)
- 🧠 CLI intuitiva con `argparse`

---

## 💻 Requisitos

- **Python 3.8+**
- **Sistema operativo Linux** (solo requerido para `udp-spoof`)
- **Permisos root** (solo para `udp-spoof`)
- **Librerías estándar de Python + `psutil`**

---

## 🔧 Instalación Manual

1. **Clona el repositorio:**
   ```bash
   git clone https://github.com/tu_usuario/universal-stress-tester.git
   cd universal-stress-tester
   ```

2. **(Opcional) Crea un entorno virtual:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Instala dependencias manualmente (sin `requirements.txt`):**
   ```bash
   python3 -m pip install psutil
   ```

---

## ▶️ Uso

Ejecuta el script principal con:

```bash
python3 stress_tester.py <modo> <host> [opciones]
```

Por ejemplo:

```bash
python3 stress_tester.py udp 192.168.1.50 -p 7777 -d 60 --min-pkt 512 --max-pkt 1024 -c 200 -P 4
```

---

## 🧨 Modos de Ataque

| Modo        | Descripción                                                |
|-------------|------------------------------------------------------------|
| `udp`       | Flood UDP genérico                                         |
| `tcp`       | Flood TCP genérico                                         |
| `udp-spoof` | UDP flood con IPs falsificadas (raw sockets, requiere root)|
| `samp`      | Handshake spam para servidores SAMP/MTA                    |
| `mc`        | Handshake + status spam para servidores Minecraft          |
| `combo`     | Ejecuta `udp`, `tcp`, `samp` y `mc` simultáneamente        |

---

## ⚙️ Configuración Avanzada

| Parámetro           | Descripción                                                             |
|---------------------|-------------------------------------------------------------------------|
| `-p, --port`         | Puerto de destino (por defecto: 25565)                                 |
| `-d, --duration`     | Duración del ataque en segundos                                        |
| `--delay`            | Tiempo base entre paquetes (segundos, por defecto: 0.01)               |
| `--jitter`           | Variación aleatoria sobre el delay (`±`, por defecto: 0.005)           |
| `--min-pkt`          | Tamaño mínimo de los paquetes en bytes                                 |
| `--max-pkt`          | Tamaño máximo de los paquetes en bytes                                 |
| `-c, --concurrency`  | Hilos asíncronos por proceso (`cpu_count() * 50` por defecto)          |
| `-P, --processes`    | Número de procesos a lanzar (`cpu_count()` por defecto)                |

---

## 🧪 Ejemplos

### 1. UDP Flood por 30 segundos, paquetes de 1 KB:
```bash
python3 stress_tester.py udp 10.0.0.5 -p 7777 -d 30 --min-pkt 1024 --max-pkt 1024
```

### 2. Ataque combinado en servidores SAMP y Minecraft:
```bash
python3 stress_tester.py combo example.com -d 45 --delay 0.02 -c 100 -P 2
```

### 3. UDP spoofing (requiere root y Linux):
```bash
sudo python3 stress_tester.py udp-spoof 192.168.0.100 -p 7777 -d 60
```

---

## ⚠️ Disclaimer

Este software se proporciona únicamente con fines **educativos y de prueba en laboratorios controlados**. **Queda totalmente prohibido** su uso sin autorización sobre sistemas que no te pertenezcan.

> **El mal uso de este script puede tener consecuencias legales. Úsalo con responsabilidad.**

---

## 📄 Licencia

Este proyecto está bajo licencia **MIT**. Consulta el archivo [`LICENSE`](LICENSE) para más información.
