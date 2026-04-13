#!/usr/bin/env python3
"""
Terminal Web + VS Code Server - Versão Render (sem interação)
"""
import os
import sys
import json
import subprocess
import urllib.request
import tarfile
import tempfile
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)

# ============================================
# INSTALAÇÃO AUTOMÁTICA DO VS CODE SERVER
# ============================================
def install_vscode_server():
    """Instala code-server (VS Code no navegador) sem interação"""
    print("[1/4] Baixando code-server...")
    
    # Criar diretório
    os.makedirs("/opt/code-server", exist_ok=True)
    
    # Baixar
    url = "https://github.com/coder/code-server/releases/download/v4.19.0/code-server-4.19.0-linux-amd64.tar.gz"
    tar_path = "/tmp/code-server.tar.gz"
    
    try:
        urllib.request.urlretrieve(url, tar_path)
        
        # Extrair
        print("[2/4] Extraindo code-server...")
        with tarfile.open(tar_path, "r:gz") as tar:
            tar.extractall("/tmp")
        
        # Mover arquivos
        subprocess.run("cp -r /tmp/code-server-*/* /opt/code-server/", shell=True, check=True)
        
        # Configurar sem senha
        config_dir = os.path.expanduser("~/.config/code-server")
        os.makedirs(config_dir, exist_ok=True)
        
        with open(f"{config_dir}/config.yaml", "w") as f:
            f.write("bind-addr: 0.0.0.0:8080\nauth: none\ncert: false\n")
        
        print("[2/4] ✅ code-server instalado!")
        return True
    except Exception as e:
        print(f"[ERRO] Falha ao instalar code-server: {e}")
        return False

def create_terminal_html():
    """Cria interface web do terminal"""
    print("[3/4] Criando interface web...")
    
    html_content = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Terminal Web - Render</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: #0a0a0a;
            color: #00ff00;
            font-family: 'Courier New', monospace;
            padding: 15px;
            min-height: 100vh;
        }
        .header {
            display: flex;
            gap: 20px;
            padding: 10px;
            background: #1a1a1a;
            margin-bottom: 20px;
            border-radius: 5px;
        }
        .header a {
            color: #00ffff;
            text-decoration: none;
            padding: 5px 15px;
            border-radius: 3px;
        }
        .header a:hover {
            background: #333;
        }
        #output {
            margin-bottom: 15px;
            max-height: calc(100vh - 150px);
            overflow-y: auto;
        }
        .line {
            margin: 3px 0;
            white-space: pre-wrap;
            word-break: break-all;
        }
        .input-line {
            display: flex;
            align-items: center;
            flex-wrap: wrap;
        }
        .green { color: #00ff00; }
        .white { color: #ffffff; }
        .blue { color: #0088ff; }
        .yellow { color: #ffff00; }
        .red { color: #ff4444; }
        .gray { color: #888888; }
        
        #cmd-input {
            background: transparent;
            border: none;
            color: #ffffff;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            outline: none;
            flex: 1;
            min-width: 200px;
            margin-left: 8px;
        }
        
        ::-webkit-scrollbar {
            width: 8px;
        }
        ::-webkit-scrollbar-track {
            background: #1a1a1a;
        }
        ::-webkit-scrollbar-thumb {
            background: #00ff00;
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <div class="header">
        <a href="/">💻 Terminal</a>
        <a href="/vscode" target="_blank">📝 VS Code</a>
        <span style="flex:1;text-align:right;color:#888" id="status">🟢 Online</span>
    </div>
    
    <div id="output"></div>
    
    <div class="input-line">
        <span class="green">user@render</span>
        <span class="white">:</span>
        <span class="blue">~</span>
        <span class="white">$</span>
        <input type="text" id="cmd-input" autofocus spellcheck="false" autocomplete="off">
    </div>

    <script>
        const output = document.getElementById('output');
        const input = document.getElementById('cmd-input');
        let history = [];
        let historyIndex = 0;
        
        function addLine(text, className = 'white') {
            const p = document.createElement('div');
            p.className = `line ${className}`;
            p.textContent = text;
            output.appendChild(p);
            output.scrollTop = output.scrollHeight;
        }
        
        async function executeCommand(cmd) {
            try {
                const response = await fetch('/execute', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({command: cmd})
                });
                const data = await response.json();
                return data.output || '';
            } catch (e) {
                return 'Erro: ' + e.message;
            }
        }
        
        async function handleCommand() {
            const cmd = input.value.trim();
            
            // Mostrar comando digitado
            addLine(`user@render:~$ ${cmd}`, 'white');
            
            if (cmd) {
                history.push(cmd);
                historyIndex = history.length;
                
                if (cmd === 'clear') {
                    output.innerHTML = '';
                } else if (cmd === 'help') {
                    addLine('Comandos disponiveis:', 'yellow');
                    addLine('  clear  - limpa a tela', 'gray');
                    addLine('  ls     - lista arquivos', 'gray');
                    addLine('  pwd    - mostra diretorio atual', 'gray');
                    addLine('  cat    - mostra conteudo de arquivo', 'gray');
                    addLine('  echo   - exibe texto', 'gray');
                    addLine('  python - executa Python', 'gray');
                } else {
                    const result = await executeCommand(cmd);
                    if (result) {
                        result.split('\\n').forEach(line => addLine(line, 'white'));
                    }
                }
            }
            
            input.value = '';
        }
        
        input.addEventListener('keydown', async (e) => {
            if (e.key === 'Enter') {
                await handleCommand();
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                if (historyIndex > 0) {
                    historyIndex--;
                    input.value = history[historyIndex];
                }
            } else if (e.key === 'ArrowDown') {
                e.preventDefault();
                if (historyIndex < history.length - 1) {
                    historyIndex++;
                    input.value = history[historyIndex];
                } else {
                    historyIndex = history.length;
                    input.value = '';
                }
            }
        });
        
        // Mensagens iniciais
        addLine('╔════════════════════════════════════════════╗', 'green');
        addLine('║   TERMINAL WEB - RENDER DEPLOY            ║', 'green');
        addLine('╚════════════════════════════════════════════╝', 'green');
        addLine('Digite "help" para comandos', 'yellow');
        addLine('');
        
        // Verificar status
        fetch('/status').then(r => r.json()).then(d => {
            document.getElementById('status').textContent = '🟢 ' + d.status;
        });
    </script>
</body>
</html>"""
    
    with open("index.html", "w") as f:
        f.write(html_content)
    
    print("[3/4] ✅ Interface criada!")

def start_vscode_server():
    """Inicia code-server em background"""
    print("[4/4] Iniciando VS Code Server...")
    try:
        subprocess.Popen(
            ["/opt/code-server/bin/code-server", "--bind-addr", "0.0.0.0:8080", "--auth", "none"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print("[4/4] ✅ VS Code Server rodando na porta 8080!")
    except:
        print("[4/4] ⚠️ VS Code Server não iniciado")

# ============================================
# ROTAS FLASK
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
        
        # Comandos bloqueados
        blocked = ['rm -rf /', ':(){ :|:& };:', 'dd if=/dev/zero', 'mkfs', 'format']
        for b in blocked:
            if b in cmd.lower():
                return jsonify({'output': f'❌ Comando bloqueado: {cmd}'})
        
        # Executar
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
            cwd='/workspace' if os.path.exists('/workspace') else '.'
        )
        
        output = result.stdout
        if result.stderr:
            output += result.stderr
            
        return jsonify({'output': output if output else '(sem saida)'})
        
    except subprocess.TimeoutExpired:
        return jsonify({'output': '⏱️ Timeout: comando excedeu 30 segundos'})
    except Exception as e:
        return jsonify({'output': f'❌ Erro: {str(e)}'})

@app.route('/status')
def status():
    return jsonify({
        'status': 'online',
        'cwd': os.getcwd(),
        'vscode': 'http://localhost:8080'
    })

# ============================================
# MAIN - Execução principal
# ============================================
if __name__ == '__main__':
    print("=" * 50)
    print("   RENDER DEPLOY - Terminal + VS Code")
    print("=" * 50)
    
    # Instalar tudo automaticamente
    install_vscode_server()
    create_terminal_html()
    start_vscode_server()
    
    print("\n" + "=" * 50)
    print("✅ DEPLOY CONCLUÍDO!")
    print("=" * 50)
    print("📁 Terminal: http://0.0.0.0:10000")
    print("💻 VS Code: http://0.0.0.0:8080")
    print("=" * 50 + "\n")
    
    # Iniciar Flask
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
