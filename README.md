# 🚀 Game Server Load Testing Framework

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-linux%20%7C%20macos%20%7C%20windows-lightgrey.svg)](https://www.python.org/)

Framework orientado a pruebas legítimas de carga y rendimiento para servidores de juegos y servicios de red en entornos autorizados. Diseñado para laboratorios, QA, benchmarking interno y validación de infraestructura.

Esta versión implementa una arquitectura híbrida basada en `multiprocessing` y `asyncio` para simular clientes concurrentes de manera eficiente, permitiendo medir estabilidad, latencia y comportamiento bajo carga controlada.

---

## 📌 Características Principales

- Arquitectura híbrida usando `multiprocessing` y `asyncio`.
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

## 🏗️ Arquitectura

1. **CLI Parser:** Procesa argumentos y configura el entorno.
2. **Worker Processes:** Distribuye carga entre múltiples núcleos.
3. **Async Event Loop:** Maneja conexiones concurrentes.
4. **Metrics Engine:** Recolecta métricas del sistema y rendimiento.

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

### Simulación de clientes concurrentes

```bash
python3 load_framework.py 192.168.1.100 -p 25565 -c 50
```

### Benchmark multi-core

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

## ⚠️ Aviso Legal

Este proyecto está destinado exclusivamente a pruebas legítimas de rendimiento, QA y validación de infraestructura en entornos autorizados.

No debe utilizarse para afectar la disponibilidad de servicios de terceros ni para actividades que violen leyes, políticas de proveedores o normativas de ciberseguridad.

El autor no se responsabiliza por usos indebidos del software.
