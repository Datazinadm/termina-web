#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Instalador automatico do sshx
Baixa e executa curl -sSf https://sshx.io/get | sh
"""
import os
import sys
import subprocess
import platform

print("=" * 50)
print("  SSHX - INSTALADOR AUTOMATICO")
print("=" * 50)

SYSTEM = platform.system()

def install_sshx():
    """Baixa e instala sshx"""
    
    print("\n[1/2] Instalando sshx...")
    
    if SYSTEM == "Windows":
        print("⚠️ sshx nao funciona no Windows")
        print("Use ngrok: https://ngrok.com")
        print("Ou WSL: wsl --install")
        return False
    
    # Linux/Mac
    cmd = "curl -sSf https://sshx.io/get | sh"
    print(f"Executando: {cmd}")
    
    result = subprocess.run(cmd, shell=True, capture_output=False)
    
    if result.returncode == 0:
        print("\n[1/2] ✅ sshx instalado com sucesso!")
        return True
    else:
        print("\n[1/2] ❌ Erro na instalacao")
        return False

def run_sshx(port=3000):
    """Executa sshx na porta especificada"""
    
    print(f"\n[2/2] Iniciando sshx na porta {port}...")
    
    # Verificar se sshx esta disponivel
    sshx_paths = [
        "sshx",
        os.path.expanduser("~/.sshx/sshx"),
        os.path.expanduser("~/.local/bin/sshx"),
        "/usr/local/bin/sshx"
    ]
    
    sshx_cmd = None
    for path in sshx_paths:
        result = subprocess.run(f"which {path} 2>/dev/null || command -v {path} 2>/dev/null", 
                               shell=True, capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            sshx_cmd = result.stdout.strip()
            break
    
    if not sshx_cmd:
        sshx_cmd = "sshx"  # Tentar mesmo assim
    
    print(f"Usando: {sshx_cmd}")
    print(f"\n{'='*50}")
    print("  SSHX INICIADO!")
    print(f"{'='*50}")
    print(f"Comando: {sshx_cmd} {port}")
    print(f"{'='*50}\n")
    
    # Executar sshx
    subprocess.run(f"{sshx_cmd} {port}", shell=True)

def main():
    """Funcao principal"""
    
    # Porta (pode ser passada como argumento)
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
    
    # Instalar sshx
    if install_sshx():
        # Rodar sshx
        run_sshx(port)
    else:
        print("\n❌ Falha na instalacao do sshx")
        sys.exit(1)

if __name__ == "__main__":
    main()
