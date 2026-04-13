#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SSHX para Render - Instalação manual sem root
"""
import os
import sys
import urllib.request
import tarfile
import tempfile
import shutil
import subprocess

print("=" * 50)
print("  SSHX RENDER - INSTALADOR MANUAL")
print("=" * 50)

HOME = os.path.expanduser("~")
SSHX_DIR = os.path.join(HOME, "sshx-bin")
SSHX_BIN = os.path.join(SSHX_DIR, "sshx")

def install_sshx():
    """Baixa e extrai sshx manualmente"""
    
    print("\n[1/3] Baixando sshx...")
    
    # Criar diretório
    os.makedirs(SSHX_DIR, exist_ok=True)
    
    # URL do sshx
    url = "https://s3.amazonaws.com/sshx/sshx-x86_64-unknown-linux-musl.tar.gz"
    tar_path = os.path.join(tempfile.gettempdir(), "sshx.tar.gz")
    
    try:
        # Baixar
        urllib.request.urlretrieve(url, tar_path)
        print("[1/3] ✅ Download concluído")
        
        # Extrair
        print("[2/3] Extraindo...")
        with tarfile.open(tar_path, "r:gz") as tar:
            # Extrair apenas o binário sshx (ignorar arquivos ._*)
            for member in tar.getmembers():
                if member.name == "sshx" or member.name.endswith("/sshx"):
                    member.name = "sshx"  # Renomear para evitar caminhos
                    tar.extract(member, SSHX_DIR)
                    break
        
        # Tornar executável
        if os.path.exists(SSHX_BIN):
            os.chmod(SSHX_BIN, 0o755)
            print(f"[2/3] ✅ sshx extraído para {SSHX_BIN}")
        else:
            print("[2/3] ❌ sshx não encontrado no arquivo")
            return False
        
        # Limpar
        os.remove(tar_path)
        return True
        
    except Exception as e:
        print(f"[ERRO] {e}")
        return False

def run_sshx():
    """Executa sshx"""
    
    port = os.environ.get('PORT', '3000')
    print(f"\n[3/3] Iniciando sshx na porta {port}...")
    
    if not os.path.exists(SSHX_BIN):
        print("[3/3] ❌ sshx não encontrado")
        return False
    
    print("\n" + "=" * 50)
    print("  ✅ SSHX INICIADO!")
    print("=" * 50)
    print(f"📍 Porta: {port}")
    print(f"🔗 URL aparecerá abaixo:")
    print("=" * 50 + "\n")
    
    # Executar
    os.system(f"{SSHX_BIN} {port}")

if __name__ == "__main__":
    if install_sshx():
        run_sshx()
    else:
        print("\n❌ Falha na instalação")
        sys.exit(1)
