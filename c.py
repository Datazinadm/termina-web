#!/usr/bin/env python3
"""
Render Deploy - Terminal Web + code-server (VS Code no navegador)
Instala tudo automaticamente no Render
"""
import os
import sys
import json
import subprocess
import urllib.request
import shutil
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)

# ============================================
# INSTALAÇÃO AUTOMÁTICA (roda no startup)
# ============================================
def install_code_server():
    """Instala code-server (VS Code no navegador)"""
    print("[1/3] Instalando code-server...")
    
    # Baixar code-server
    url = "https://github.com/coder/code-server/releases/download/v4.19.0/code-server-4.19.0-linux-amd64.tar.gz"
    tar_path = "/tmp/code-server.tar.gz"
    
    urllib.request.urlretrieve(url, tar_path)
    subprocess.run(f"tar -xzf {tar_path} -C /tmp", shell=True)
    
    # Mover para /opt
    subprocess.run("mkdir -p /opt/code-server", shell=True)
    subprocess.run("cp -r /tmp/code-server-*/* /opt/code-server/", shell=True)
    
    # Criar diretório de configuração
    subprocess.run("mkdir -p ~/.config/code-server", shell=True)
    
    # Configuração básica (sem senha)
    config = """
bind-addr: 0.0.0.0:8080
auth: none
cert: false
"""
    with open(os.path.expanduser("~/.config/code-server/config.yaml"), "w") as f:
        f.write(config)
    
    print("[1/3] ✅ code-server instalado!")

def create_terminal_files():
    """Cria arquivos do terminal web"""
    print("[2/3] Criando arquivos do terminal...")
    
    # index.html
    with open("index.html", "w") as f:
        f.write("""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Terminal Web</title>
    <style>
        body{background:#000;color:#0f0;font-family:monospace;padding:10px}
        input{background:#000;color:#fff;border:none;outline:none;font:14px monospace;width:80%}
        #out{margin-bottom:10px}p{margin:2px 0;white-space:pre-wrap}
        .g{color:#0f0}.w{color:#fff}.b{color:#08f}.y{color:#ff0}
        .menu{position:fixed;top:10px;right:10px}
        .menu a{color:#0ff;margin:0 10px;text-decoration:none}
    </style>
</head>
<body>
<div class="menu">
    <a href="/">Terminal</a>
    <a href="/vscode" target="_blank">VS Code</a>
</div>
<div id="out"></div>
<script>
let hist=[],c=0;
function addLine(t,c){let p=document.createElement("p");p.textContent=t;p.className=c;out.appendChild(p)}
function prompt(){
let d=document.createElement("div");d.id="sp";
d.innerHTML='<span class="g">user@render</span><span class="w">:</span><span class="b">~</span><span class="w">$</span> ';
let i=document.createElement("input");i.id="in";i.spellcheck=false;
d.appendChild(i);document.body.appendChild(d);i.focus()
}
async function exec(cmd){
try{
let r=await fetch('/execute',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({command:cmd})});
let d=await r.json();return d.output
}catch(e){return 'Erro'}
}
async function send(){
let v=document.getElementById('in').value;
addLine('user@render:~$ '+v,'w');
if(v.trim())hist.push(v);
document.getElementById('in').value='';c=hist.length;
if(v=='clear'){out.innerHTML=''}else if(v){addLine(await exec(v),'w')}
document.getElementById('sp').scrollIntoView()
}
document.addEventListener('keydown',e=>{
if(e.key=='Enter')send();
if(e.key=='ArrowUp'){e.preventDefault();if(c>0)c--;document.getElementById('in').value=hist[c]||''}
if(e.key=='ArrowDown'){e.preventDefault();if(c<hist.length-1)c++;else{document.getElementById('in').value='';c=hist.length}}
});
addLine('Terminal Web Render - Comandos Linux','y');
addLine('clear = limpa | <a href="/vscode" target="_blank">Abrir VS Code</a>','y');
prompt();
</script>
</body></html>""")
    
    print("[2/3] ✅ Arquivos criados!")

def start_code_server():
    """Inicia code-server em background"""
    print("[3/3] Iniciando code-server na porta 8080...")
    subprocess.Popen([
        "/opt/code-server/bin/code-server",
        "--bind-addr", "0.0.0.0:8080",
        "--auth", "none",
        "/workspace"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("[3/3] ✅ code-server rodando!")

# ============================================
# ROTAS DO FLASK
# ============================================
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/execute', methods=['POST'])
def execute():
    try:
        data = request.get_json()
        cmd = data.get('command', '').strip()
        if not cmd:
            return jsonify({'output': ''})
        
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        output = result.stdout + result.stderr
        return jsonify({'output': output})
    except Exception as e:
        return jsonify({'output': str(e)})

@app.route('/status')
def status():
    return jsonify({'status': 'online', 'vscode': 'http://localhost:8080'})

# ============================================
# INICIALIZAÇÃO
# ============================================
if __name__ == '__main__':
    print("=" * 50)
    print("  RENDER DEPLOY - Terminal + VS Code")
    print("=" * 50)
    
    # Instalar tudo
    install_code_server()
    create_terminal_files()
    start_code_server()
    
    print("\n✅ TUDO PRONTO!")
    print("📁 Terminal: http://0.0.0.0:10000")
    print("💻 VS Code: http://0.0.0.0:8080")
    print("=" * 50)
    
    # Iniciar servidor Flask
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
