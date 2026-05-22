# 🚀 Universal Game Server Load Testing Framework v3

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-linux%20%7C%20macos%20%7C%20windows-lightgrey.svg)](https://www.python.org/)

Framework orientado a pruebas legítimas de carga, benchmarking y validación de infraestructura para servidores de juegos y servicios de red en entornos autorizados. Diseñado para laboratorios, QA, auditorías internas y desarrollo de mecanismos de resiliencia y mitigación.

Esta versión implementa una arquitectura híbrida basada en `multiprocessing`, `asyncio` y sockets no bloqueantes, permitiendo generar carga controlada de alta concurrencia para medir estabilidad, latencia, throughput y comportamiento bajo presión operativa.

---

## 📌 Características Principales

- Arquitectura híbrida usando `multiprocessing`, `asyncio` y sockets no bloqueantes.
- Escalado multi-core para aprovechar todos los núcleos disponibles.
- Pools de memoria precalculados para reducir overhead del GC.
- Sistema de telemetría en tiempo real por proceso.
- Simulación de conexiones concurrentes para pruebas internas controladas.
- Soporte para conexiones concurrentes no bloqueantes.
- Simulación de tráfico legítimo para pruebas internas.
- Telemetría en tiempo real:
  - Operaciones por segundo.
  - Uso de CPU.
  - Consumo de memoria.
  - Conexiones activas.
- Configuración flexible de concurrencia y duración.
- Compatible con Linux, macOS y Windows.

---

## 🏗️ Arquitectura y Flujo de Ejecución

1. **CLI Parser:** Procesa argumentos y configura el entorno de ejecución.
2. **Master Processes:** Distribuye workers entre múltiples núcleos para evitar limitaciones del GIL.
3. **Async Event Loop:** Gestiona conexiones y sockets concurrentes de forma eficiente.
4. **Memory Pools:** Utiliza payloads y delays precalculados para minimizar asignaciones dinámicas.
5. **Metrics Engine:** Recolecta métricas de rendimiento, CPU y throughput.

---

## 🚀 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/game-server-load-framework.git
cd game-server-load-framework
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Dependencias opcionales

```bash
pip install psutil
```

---

## 💻 Uso

```bash
python3 load_framework.py [opciones] host
```

### Parámetros principales

| Parámetro | Descripción |
|---|---|
| `-p, --port` | Puerto destino |
| `-d, --duration` | Duración de la prueba |
| `-c, --concurrency` | Clientes concurrentes |
| `-P, --processes` | Procesos paralelos |
| `--delay` | Retardo entre operaciones |

---

## 🛠️ Ejemplos

### Simulación de clientes concurrentes (Laboratorio)

```bash
python3 load_framework.py 192.168.1.100 -p 25565 -c 50
```

### Benchmark multi-core de infraestructura

```bash
python3 load_framework.py 10.0.0.5 -P 8 -c 100
```

---

## 📊 Métricas de Salida

```text
[*] Inicializando entorno de pruebas...
[*] Procesos activos: 8
[*] Clientes concurrentes: 50
[INFO] Ops/s: 12500 | CPU: 82% | RAM: 410MB
```

---

## 🔒 Buenas Prácticas

- Ejecutar únicamente sobre infraestructura propia o autorizada.
- Definir límites de concurrencia razonables.
- Supervisar consumo de recursos durante pruebas.
- Documentar resultados y métricas obtenidas.

---

## ⚠️ Aviso Legal y Uso Responsable

Este proyecto está destinado exclusivamente a pruebas legítimas de rendimiento, QA y validación de infraestructura en entornos autorizados.

No debe utilizarse contra infraestructura de terceros sin autorización explícita. El uso indebido de herramientas de generación de carga o saturación puede violar leyes de ciberseguridad, términos de servicio y regulaciones internacionales.

El autor no se responsabiliza por usos indebidos del software.
