#!/usr/bin/env python3
import os, sys, platform, subprocess, time, urllib.request, tempfile, shutil

SYSTEM = platform.system()
PROJECT_DIR = os.path.join(os.path.expanduser("~"), "terminal-web")

def run(cmd, silent=False):
    """Executa comando sem mostrar saida"""
    try:
        if SYSTEM == "Windows":
            subprocess.run(cmd, shell=True, capture_output=silent, 
                          creationflags=subprocess.CREATE_NO_WINDOW)
        else:
            subprocess.run(cmd, shell=True, capture_output=silent)
        return True
    except:
        return False

def check_node():
    """Verifica/instala Node.js automaticamente"""
    if run("node --version", silent=True):
        return True
    
    print("[1/5] Instalando Node.js...")
    
    if SYSTEM == "Windows":
        url = "https://nodejs.org/dist/v20.11.0/node-v20.11.0-x64.msi"
        msi = os.path.join(tempfile.gettempdir(), "node.msi")
        urllib.request.urlretrieve(url, msi)
        run(f'msiexec /i "{msi}" /quiet /norestart')
        time.sleep(30)
        os.remove(msi)
    
    elif SYSTEM == "Linux":
        if os.path.exists("/etc/debian_version"):
            run("sudo apt update -y && sudo apt install -y curl")
            run("curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -")
            run("sudo apt install -y nodejs")
        else:
            run("curl -fsSL https://rpm.nodesource.com/setup_20.x | sudo bash -")
            run("sudo yum install -y nodejs")
    
    elif SYSTEM == "Darwin":
        run("brew install node")
    
    return True

def create_files():
    """Cria arquivos do projeto"""
    print("[2/5] Criando arquivos...")
    
    os.makedirs(PROJECT_DIR, exist_ok=True)
    os.chdir(PROJECT_DIR)
    
    # package.json
    with open("package.json", "w") as f:
        f.write('{"name":"terminal-web","dependencies":{"express":"^4.18.2"}}')
    
    # server.js
    with open("server.js", "w", encoding="utf-8") as f:
        f.write("""
const express = require('express');
const { exec } = require('child_process');
const os = require('os');
const app = express();
app.use(express.json());
app.use(express.static(__dirname));

app.post('/execute', (req, res) => {
    const cmd = req.body.command || '';
    if (!cmd.trim()) return res.json({output: ''});
    
    const shell = os.platform() === 'win32' ? 'cmd.exe' : '/bin/bash';
    exec(cmd, {shell, timeout: 30000, maxBuffer: 50*1024*1024}, (err, out, serr) => {
        res.json({output: out + (serr || (err ? err.message : ''))});
    });
});

app.listen(3000, () => console.log('Servidor: http://localhost:3000'));
""")
    
    # index.html
    with open("index.html", "w", encoding="utf-8") as f:
        f.write("""
<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Terminal Web</title>
<style>
body{background:#000;color:#0f0;font-family:monospace;padding:10px;margin:0}
input{background:#000;color:#fff;border:none;outline:none;font:14px monospace;width:80%}
#out{margin-bottom:10px}p{margin:2px 0;white-space:pre-wrap}
.g{color:#0f0}.w{color:#fff}.b{color:#08f}.y{color:#ff0}.r{color:#f44}
</style></head>
<body><div id="out"></div>
<script>
let hist=[],c=0;
function addLine(t,css){let p=document.createElement("p");p.textContent=t;p.className=css;out.appendChild(p)}
function prompt(){let d=document.createElement("div");d.id="sp";
d.innerHTML='<span class="g">user@term</span><span class="w">:</span><span class="b">~</span><span class="w">$</span> ';
let i=document.createElement("input");i.id="in";i.spellcheck=false;d.appendChild(i);document.body.appendChild(d);i.focus()}
async function exec(cmd){
try{let r=await fetch('/execute',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({command:cmd})});
let d=await r.json();return d.output}catch(e){return 'Erro: servidor offline'}}
async function send(){
let v=document.getElementById('in').value;
addLine('user@term:~$ '+v,'w');
if(v.trim())hist.push(v);
document.getElementById('in').value='';c=hist.length;
if(v=='clear'){out.innerHTML=''}else if(v){addLine(await exec(v),'w')}
document.getElementById('sp').scrollIntoView()}
document.addEventListener('keydown',e=>{
if(e.key=='Enter')send();
if(e.key=='ArrowUp'){e.preventDefault();if(c>0)c--;document.getElementById('in').value=hist[c]||''}
if(e.key=='ArrowDown'){e.preventDefault();if(c<hist.length-1)c++;else{document.getElementById('in').value='';c=hist.length}}
});
addLine('Terminal Web - Digite comandos do sistema','y');
addLine('clear = limpa | comandos Windows/Linux/Mac','y');
prompt();
</script></body></html>
""")

def install_deps():
    """Instala dependencias npm"""
    print("[3/5] Instalando dependencias...")
    os.chdir(PROJECT_DIR)
    run("npm install --silent", silent=True)

def install_tunnel():
    """Instala ferramenta de tunel (ngrok no Windows, sshx no Linux/Mac)"""
    print("[4/5] Instalando tunel...")
    
    if SYSTEM == "Windows":
        # Ngrok para Windows
        ngrok_path = os.path.join(os.environ.get("USERPROFILE", ""), "ngrok.exe")
        if not os.path.exists(ngrok_path):
            url = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip"
            zip_path = os.path.join(tempfile.gettempdir(), "ngrok.zip")
            urllib.request.urlretrieve(url, zip_path)
            import zipfile
            with zipfile.ZipFile(zip_path, 'r') as z:
                z.extract("ngrok.exe", os.path.dirname(ngrok_path))
            os.remove(zip_path)
    else:
        # Sshx para Linux/Mac
        run("curl -sSf https://sshx.io/get | sh -s -- -y 2>/dev/null", silent=True)

def start_server():
    """Inicia o servidor e tunel"""
    print("[5/5] Iniciando servidor...")
    os.chdir(PROJECT_DIR)
    
    if SYSTEM == "Windows":
        # Windows: abre node em nova janela e ngrok em outra
        subprocess.Popen("start cmd /k node server.js", shell=True)
        time.sleep(3)
        ngrok = os.path.join(os.environ.get("USERPROFILE", ""), "ngrok.exe")
        if os.path.exists(ngrok):
            subprocess.Popen(f"start cmd /k {ngrok} http 3000", shell=True)
            print("\n✅ SERVIDOR INICIADO!")
            print("📁 Local: http://localhost:3000")
            print("🌍 Publico: Verifique a janela do ngrok")
    else:
        # Linux/Mac: abre em terminal separado
        if SYSTEM == "Linux":
            subprocess.Popen(["x-terminal-emulator", "-e", "node server.js"])
            time.sleep(3)
            subprocess.Popen(["x-terminal-emulator", "-e", "sshx 3000"])
        elif SYSTEM == "Darwin":
            subprocess.Popen(["osascript", "-e", 'tell app "Terminal" to do script "node ' + 
                             os.path.join(PROJECT_DIR, "server.js") + '"'])
            time.sleep(3)
            subprocess.Popen(["osascript", "-e", 'tell app "Terminal" to do script "sshx 3000"'])
        
        print("\n✅ SERVIDOR INICIADO!")
        print("📁 Local: http://localhost:3000")
        print("🌍 Publico: Verifique a janela do sshx")
    
    print("\nPressione Ctrl+C para encerrar tudo")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nEncerrando...")
        if SYSTEM == "Windows":
            run("taskkill /f /im node.exe")
            run("taskkill /f /im ngrok.exe")

if __name__ == "__main__":
    print("=" * 50)
    print("  TERMINAL WEB - Instalador Automatico")
    print("=" * 50)
    
    check_node()
    create_files()
    install_deps()
    install_tunnel()
    start_server()
