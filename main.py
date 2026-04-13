#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Termux Web - Comandos de Uma Letra + Teclado Completo
Version: 5.0.0
"""

from flask import Flask, render_template_string, request, session, redirect, url_for
import subprocess
import os
import sys
import platform
from datetime import datetime
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

# Configuration
SYSTEM_NAME = platform.node()
OS_TYPE = platform.system()
CURRENT_USER = os.getenv('USER') or os.getenv('USERNAME') or 'user'
PASSWORD = 'mayara123'

LOGIN_PAGE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes">
    <title>Termux • Login</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: #000000;
            font-family: 'Courier New', monospace;
            height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .login-container {
            background: #000000;
            padding: 2rem;
            width: 90%;
            max-width: 380px;
            border: 1px solid #00ff00;
        }
        .termux-logo {
            color: #00ff00;
            font-size: 10px;
            line-height: 1.2;
            margin-bottom: 2rem;
            text-align: center;
            white-space: pre;
            font-family: monospace;
        }
        .input-line {
            display: flex;
            align-items: center;
            margin-bottom: 1rem;
        }
        .prompt { color: #00ff00; margin-right: 0.75rem; font-size: 0.9rem; }
        input {
            background: #000000;
            border: none;
            color: #00ff00;
            font-family: 'Courier New', monospace;
            font-size: 0.9rem;
            flex: 1;
            outline: none;
        }
        button {
            background: transparent;
            border: 1px solid #00ff00;
            color: #00ff00;
            padding: 0.5rem 1rem;
            font-family: monospace;
            cursor: pointer;
            width: 100%;
        }
        button:active { background: #00ff00; color: #000000; }
        .error-msg { color: #ff4444; margin-top: 1rem; display: none; }
        .error-msg.show { display: block; }
    </style>
</head>
<body>
    <div class="login-container">
        <div class="termux-logo">
╔══════════════════════════════╗
║        TERMUX WEB            ║
║        v5.0 COMPLETE         ║
╚══════════════════════════════╝
        </div>
        <div class="input-line">
            <span class="prompt">$></span>
            <input type="password" id="password" placeholder="password" autofocus>
        </div>
        <button onclick="authenticate()">Login</button>
        <div class="error-msg" id="errorMsg">[!] Access denied</div>
    </div>
    <script>
        async function authenticate() {
            const response = await fetch('/auth', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ password: document.getElementById('password').value })
            });
            const data = await response.json();
            if (data.success) window.location.href = '/terminal';
            else {
                document.getElementById('errorMsg').classList.add('show');
                setTimeout(() => document.getElementById('errorMsg').classList.remove('show'), 2000);
            }
        }
        document.getElementById('password').addEventListener('keypress', (e) => { if(e.key === 'Enter') authenticate(); });
    </script>
</body>
</html>
'''

TERMINAL_PAGE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes, viewport-fit=cover">
    <title>Termux • Complete</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: #000000;
            color: #00ff00;
            font-family: 'Courier New', monospace;
            height: 100vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        .status-bar {
            background: #000000;
            padding: 0.4rem 0.7rem;
            display: flex;
            justify-content: space-between;
            font-size: 0.65rem;
            color: #00ff00;
            border-bottom: 0.5px solid #00ff00;
            flex-shrink: 0;
        }
        .terminal-area {
            flex: 1;
            overflow-y: auto;
            padding: 0.5rem;
            cursor: text;
        }
        .terminal-output {
            color: #00ff00;
            font-size: 0.8rem;
            line-height: 1.3;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        .terminal-output div { margin-bottom: 0.1rem; }
        .prompt-line {
            display: flex;
            align-items: center;
            flex-wrap: wrap;
            margin-top: 0.1rem;
        }
        .prompt-text { color: #00ff00; margin-right: 0.3rem; }
        .input-cursor {
            display: inline-block;
            width: 7px;
            height: 12px;
            background-color: #00ff00;
            animation: blink 1s step-end infinite;
            vertical-align: middle;
            margin-left: 2px;
        }
        @keyframes blink { 0%,100% { opacity: 1; } 50% { opacity: 0; } }
        
        /* Teclado COMPLETO estilo celular */
        .termux-keyboard {
            background: #000000;
            border-top: 0.5px solid #00ff00;
            padding: 0.3rem;
            flex-shrink: 0;
            max-height: 50vh;
            overflow-y: auto;
        }
        .kb-row {
            display: flex;
            gap: 0.2rem;
            margin-bottom: 0.2rem;
            flex-wrap: wrap;
            justify-content: center;
        }
        .kb-key {
            background: #001100;
            border: 0.5px solid #00ff00;
            color: #00ff00;
            padding: 0.4rem 0;
            text-align: center;
            font-family: monospace;
            font-size: 0.65rem;
            font-weight: bold;
            border-radius: 3px;
            cursor: pointer;
            flex: 1;
            min-width: 35px;
            user-select: none;
        }
        .kb-key:active { background: #00ff00; color: #000000; transform: scale(0.95); }
        .kb-special { color: #ffaa00; border-color: #ffaa00; }
        .kb-number { color: #00ffaa; border-color: #00ffaa; }
        .kb-symbol { color: #ff66ff; border-color: #ff66ff; }
        .kb-wide { flex: 2; min-width: 60px; }
        .kb-extra-wide { flex: 3; min-width: 80px; }
        
        @media (max-width: 600px) {
            .terminal-area { padding: 0.4rem; }
            .terminal-output { font-size: 0.7rem; }
            .kb-key { font-size: 0.55rem; padding: 0.35rem 0; min-width: 28px; }
        }
        ::-webkit-scrollbar { width: 3px; }
        ::-webkit-scrollbar-track { background: #000000; }
        ::-webkit-scrollbar-thumb { background: #00ff00; }
    </style>
</head>
<body>
    <div class="status-bar">
        <span>Termux • Complete Keyboard</span>
        <span>bash</span>
    </div>
    
    <div class="terminal-area" id="terminalArea">
        <div class="terminal-output" id="output">
            <div>Termux Web v5.0 - Teclado Completo</div>
            <div>Digite qualquer comando (ex: dir, d, dd, etc)</div>
            <div></div>
        </div>
    </div>
    
    <input type="text" id="hiddenInput" style="position:fixed; top:-100px; left:0; width:1px; height:1px; opacity:0;">
    
    <div class="termux-keyboard">
        <!-- NÚMEROS 0-9 -->
        <div class="kb-row">
            <div class="kb-key kb-number" data-char="0">0</div>
            <div class="kb-key kb-number" data-char="1">1</div>
            <div class="kb-key kb-number" data-char="2">2</div>
            <div class="kb-key kb-number" data-char="3">3</div>
            <div class="kb-key kb-number" data-char="4">4</div>
            <div class="kb-key kb-number" data-char="5">5</div>
            <div class="kb-key kb-number" data-char="6">6</div>
            <div class="kb-key kb-number" data-char="7">7</div>
            <div class="kb-key kb-number" data-char="8">8</div>
            <div class="kb-key kb-number" data-char="9">9</div>
        </div>
        
        <!-- SÍMBOLOS LINHA 1 -->
        <div class="kb-row">
            <div class="kb-key kb-symbol" data-char="`">`</div>
            <div class="kb-key kb-symbol" data-char="~">~</div>
            <div class="kb-key kb-symbol" data-char="!">!</div>
            <div class="kb-key kb-symbol" data-char="@">@</div>
            <div class="kb-key kb-symbol" data-char="#">#</div>
            <div class="kb-key kb-symbol" data-char="$">$</div>
            <div class="kb-key kb-symbol" data-char="%">%</div>
            <div class="kb-key kb-symbol" data-char="^">^</div>
            <div class="kb-key kb-symbol" data-char="&">&</div>
            <div class="kb-key kb-symbol" data-char="*">*</div>
        </div>
        
        <!-- SÍMBOLOS LINHA 2 -->
        <div class="kb-row">
            <div class="kb-key kb-symbol" data-char="(">(</div>
            <div class="kb-key kb-symbol" data-char=")">)</div>
            <div class="kb-key kb-symbol" data-char="-">-</div>
            <div class="kb-key kb-symbol" data-char="_">_</div>
            <div class="kb-key kb-symbol" data-char="=">=</div>
            <div class="kb-key kb-symbol" data-char="+">+</div>
            <div class="kb-key kb-symbol" data-char="[">[</div>
            <div class="kb-key kb-symbol" data-char="]">]</div>
            <div class="kb-key kb-symbol" data-char="{">{</div>
            <div class="kb-key kb-symbol" data-char="}">}</div>
        </div>
        
        <!-- SÍMBOLOS LINHA 3 -->
        <div class="kb-row">
            <div class="kb-key kb-symbol" data-char=";">;</div>
            <div class="kb-key kb-symbol" data-char=":">:</div>
            <div class="kb-key kb-symbol" data-char="'">'</div>
            <div class="kb-key kb-symbol" data-char='"'>"</div>
            <div class="kb-key kb-symbol" data-char=",">,</div>
            <div class="kb-key kb-symbol" data-char="<"><</div>
            <div class="kb-key kb-symbol" data-char=".">.</div>
            <div class="kb-key kb-symbol" data-char=">">></div>
            <div class="kb-key kb-symbol" data-char="?">?</div>
            <div class="kb-key kb-symbol" data-char="/">/</div>
        </div>
        
        <!-- LETRAS QWERTYUIOP minúsculas -->
        <div class="kb-row">
            <div class="kb-key" data-char="q">q</div><div class="kb-key" data-char="w">w</div>
            <div class="kb-key" data-char="e">e</div><div class="kb-key" data-char="r">r</div>
            <div class="kb-key" data-char="t">t</div><div class="kb-key" data-char="y">y</div>
            <div class="kb-key" data-char="u">u</div><div class="kb-key" data-char="i">i</div>
            <div class="kb-key" data-char="o">o</div><div class="kb-key" data-char="p">p</div>
        </div>
        
        <!-- LETRAS maiúsculas QWERTYUIOP -->
        <div class="kb-row">
            <div class="kb-key" data-char="Q">Q</div><div class="kb-key" data-char="W">W</div>
            <div class="kb-key" data-char="E">E</div><div class="kb-key" data-char="R">R</div>
            <div class="kb-key" data-char="T">T</div><div class="kb-key" data-char="Y">Y</div>
            <div class="kb-key" data-char="U">U</div><div class="kb-key" data-char="I">I</div>
            <div class="kb-key" data-char="O">O</div><div class="kb-key" data-char="P">P</div>
        </div>
        
        <!-- LETRAS ASDFGHJKL minúsculas -->
        <div class="kb-row">
            <div class="kb-key" data-char="a">a</div><div class="kb-key" data-char="s">s</div>
            <div class="kb-key" data-char="d">d</div><div class="kb-key" data-char="f">f</div>
            <div class="kb-key" data-char="g">g</div><div class="kb-key" data-char="h">h</div>
            <div class="kb-key" data-char="j">j</div><div class="kb-key" data-char="k">k</div>
            <div class="kb-key" data-char="l">l</div>
        </div>
        
        <!-- LETRAS maiúsculas ASDFGHJKL -->
        <div class="kb-row">
            <div class="kb-key" data-char="A">A</div><div class="kb-key" data-char="S">S</div>
            <div class="kb-key" data-char="D">D</div><div class="kb-key" data-char="F">F</div>
            <div class="kb-key" data-char="G">G</div><div class="kb-key" data-char="H">H</div>
            <div class="kb-key" data-char="J">J</div><div class="kb-key" data-char="K">K</div>
            <div class="kb-key" data-char="L">L</div>
        </div>
        
        <!-- LETRAS ZXCVBNM minúsculas -->
        <div class="kb-row">
            <div class="kb-key" data-char="z">z</div><div class="kb-key" data-char="x">x</div>
            <div class="kb-key" data-char="c">c</div><div class="kb-key" data-char="v">v</div>
            <div class="kb-key" data-char="b">b</div><div class="kb-key" data-char="n">n</div>
            <div class="kb-key" data-char="m">m</div>
        </div>
        
        <!-- LETRAS maiúsculas ZXCVBNM -->
        <div class="kb-row">
            <div class="kb-key" data-char="Z">Z</div><div class="kb-key" data-char="X">X</div>
            <div class="kb-key" data-char="C">C</div><div class="kb-key" data-char="V">V</div>
            <div class="kb-key" data-char="B">B</div><div class="kb-key" data-char="N">N</div>
            <div class="kb-key" data-char="M">M</div>
        </div>
        
        <!-- TECLAS ESPECIAIS -->
        <div class="kb-row">
            <div class="kb-key kb-special" data-key="escape">ESC</div>
            <div class="kb-key kb-special" data-key="tab">TAB</div>
            <div class="kb-key kb-special" data-key="ctrl">CTRL</div>
            <div class="kb-key kb-special" data-key="alt">ALT</div>
            <div class="kb-key kb-special" data-key="home">HOME</div>
            <div class="kb-key kb-special" data-key="end">END</div>
            <div class="kb-key kb-special" data-key="pageup">PGUP</div>
            <div class="kb-key kb-special" data-key="pagedown">PGDN</div>
        </div>
        
        <!-- SETAS -->
        <div class="kb-row">
            <div class="kb-key kb-special kb-wide" data-key="left">← LEFT</div>
            <div class="kb-key kb-special kb-wide" data-key="up">↑ UP</div>
            <div class="kb-key kb-special kb-wide" data-key="down">↓ DOWN</div>
            <div class="kb-key kb-special kb-wide" data-key="right">→ RIGHT</div>
        </div>
        
        <!-- BACKSPACE, SPACE, ENTER -->
        <div class="kb-row">
            <div class="kb-key kb-wide kb-special" data-key="backspace">⌫ BACKSPACE</div>
            <div class="kb-key kb-extra-wide" data-char=" ">␣ SPACE</div>
            <div class="kb-key kb-wide kb-special" data-action="execute">↵ ENTER</div>
        </div>
        
        <!-- LIMPAR TUDO -->
        <div class="kb-row">
            <div class="kb-key kb-wide kb-special" data-key="clear">🗑️ CLEAR INPUT</div>
            <div class="kb-key kb-wide kb-special" data-action="clear">🧹 CLEAR SCREEN</div>
        </div>
    </div>

    <script>
        let currentInput = '';
        let commandHistory = [];
        let historyPos = -1;
        
        const outputDiv = document.getElementById('output');
        const hiddenInput = document.getElementById('hiddenInput');
        const terminalArea = document.getElementById('terminalArea');
        
        function createPromptLine() {
            const promptLine = document.createElement('div');
            promptLine.className = 'prompt-line';
            promptLine.innerHTML = `<span class="prompt-text">{{ current_user }}@{{ system_name }}:~$ </span><span class="input-line"></span>`;
            return promptLine;
        }
        
        function updateDisplay() {
            let promptLine = outputDiv.querySelector('.prompt-line:last-child');
            if (!promptLine) {
                promptLine = createPromptLine();
                outputDiv.appendChild(promptLine);
            }
            const inputSpan = promptLine.querySelector('.input-line');
            if (currentInput === '') {
                inputSpan.innerHTML = '<span class="input-cursor"></span>';
            } else {
                inputSpan.innerHTML = escapeHtml(currentInput) + '<span class="input-cursor"></span>';
            }
            scrollToBottom();
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        function scrollToBottom() {
            terminalArea.scrollTop = terminalArea.scrollHeight;
        }
        
        function addCommandToHistory(cmd) {
            const promptLine = outputDiv.querySelector('.prompt-line:last-child');
            if (promptLine) {
                promptLine.innerHTML = `<span class="prompt-text">{{ current_user }}@{{ system_name }}:~$ </span>${escapeHtml(cmd)}`;
            }
        }
        
        function addOutput(text) {
            if (text === undefined || text === null) return;
            const outputLine = document.createElement('div');
            outputLine.style.color = '#00ff00';
            outputLine.style.whiteSpace = 'pre-wrap';
            outputLine.textContent = text;
            outputDiv.insertBefore(outputLine, outputDiv.querySelector('.prompt-line:last-child'));
            scrollToBottom();
        }
        
        function clearScreen() {
            while (outputDiv.children.length > 0) {
                outputDiv.removeChild(outputDiv.firstChild);
            }
            const initialPrompt = createPromptLine();
            outputDiv.appendChild(initialPrompt);
            updateDisplay();
        }
        
        async function executeCommand() {
            if (currentInput.trim() === '') {
                currentInput = '';
                updateDisplay();
                return;
            }
            
            const cmd = currentInput.trim();
            addCommandToHistory(cmd);
            commandHistory.push(cmd);
            historyPos = -1;
            
            if (cmd === 'exit' || cmd === 'logout') {
                window.location.href = '/logout';
                return;
            }
            
            if (cmd === 'clear' || cmd === 'cls') {
                clearScreen();
                currentInput = '';
                updateDisplay();
                return;
            }
            
            try {
                const response = await fetch('/exec', {
                    method: 'POST',
                    body: cmd
                });
                const result = await response.text();
                if (result && result.trim()) {
                    const lines = result.split('\\n');
                    for (const line of lines) {
                        if (line !== undefined && line !== null && line !== '') {
                            addOutput(line);
                        }
                    }
                }
            } catch (err) {
                addOutput(`Error: ${err.toString()}`);
            }
            
            const newPromptLine = createPromptLine();
            outputDiv.appendChild(newPromptLine);
            currentInput = '';
            updateDisplay();
            scrollToBottom();
        }
        
        function addChar(char) {
            currentInput += char;
            updateDisplay();
        }
        
        function backspace() {
            currentInput = currentInput.slice(0, -1);
            updateDisplay();
        }
        
        function clearInput() {
            currentInput = '';
            updateDisplay();
        }
        
        function historyUp() {
            if (historyPos < commandHistory.length - 1) {
                historyPos++;
                currentInput = commandHistory[commandHistory.length - 1 - historyPos];
                updateDisplay();
            }
        }
        
        function historyDown() {
            if (historyPos > 0) {
                historyPos--;
                currentInput = commandHistory[commandHistory.length - 1 - historyPos];
                updateDisplay();
            } else if (historyPos === 0) {
                historyPos = -1;
                currentInput = '';
                updateDisplay();
            }
        }
        
        // Eventos do teclado virtual
        document.querySelectorAll('.kb-key[data-char]').forEach(key => {
            key.addEventListener('click', () => addChar(key.dataset.char));
            key.addEventListener('touchstart', (e) => { e.preventDefault(); addChar(key.dataset.char); });
        });
        
        document.querySelectorAll('.kb-key[data-key]').forEach(key => {
            key.addEventListener('click', () => {
                const k = key.dataset.key;
                if (k === 'backspace') backspace();
                else if (k === 'escape' || k === 'clear') clearInput();
                else if (k === 'up') historyUp();
                else if (k === 'down') historyDown();
                else if (k === 'tab') addChar('    ');
                else if (k !== 'ctrl' && k !== 'alt') addChar(k);
            });
        });
        
        document.querySelectorAll('[data-action="execute"]').forEach(btn => {
            btn.addEventListener('click', () => executeCommand());
        });
        
        document.querySelectorAll('[data-action="clear"]').forEach(btn => {
            btn.addEventListener('click', () => { clearScreen(); currentInput = ''; updateDisplay(); });
        });
        
        terminalArea.addEventListener('click', () => { hiddenInput.focus(); });
        
        hiddenInput.addEventListener('input', (e) => {
            for (const char of e.target.value) {
                if (char === '\\n') executeCommand();
                else if (char === '\\x7f') backspace();
                else addChar(char);
            }
            hiddenInput.value = '';
        });
        
        hiddenInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') { e.preventDefault(); executeCommand(); }
            else if (e.key === 'ArrowUp') { e.preventDefault(); historyUp(); }
            else if (e.key === 'ArrowDown') { e.preventDefault(); historyDown(); }
        });
        
        setTimeout(() => {
            hiddenInput.focus();
            const initialPrompt = createPromptLine();
            outputDiv.appendChild(initialPrompt);
            updateDisplay();
        }, 100);
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    if session.get('authenticated'):
        return redirect(url_for('terminal'))
    return render_template_string(LOGIN_PAGE)

@app.route('/auth', methods=['POST'])
def auth():
    data = request.get_json()
    if data and data.get('password') == PASSWORD:
        session['authenticated'] = True
        return {'success': True}
    return {'success': False}

@app.route('/terminal')
def terminal():
    if not session.get('authenticated'):
        return redirect(url_for('index'))
    return render_template_string(
        TERMINAL_PAGE,
        system_name=SYSTEM_NAME.split('.')[0],
        current_user=CURRENT_USER
    )

@app.route('/exec', methods=['POST'])
def execute():
    if not session.get('authenticated'):
        return 'Unauthorized', 401
    
    cmd = request.data.decode('utf-8')
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
            encoding='utf-8',
            errors='replace'
        )
        output = result.stdout + result.stderr
        if not output:
            output = f'Comando "{cmd}" executado (sem saída)'
        return output
    except subprocess.TimeoutExpired:
        return 'Timeout: Comando excedeu 30 segundos'
    except Exception as e:
        return str(e)

@app.route('/logout')
def logout():
    session.pop('authenticated', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    
    print()
    print('\033[92m╔══════════════════════════════════════════════════════════╗\033[0m')
    print('\033[92m║     Termux Web - Teclado Completo + Comando de 1 Letra   ║\033[0m')
    print('\033[92m╠══════════════════════════════════════════════════════════╣\033[0m')
    print(f'\033[92m║  \033[0m🌐 URL: http://localhost:{port}\033[92m{ " " * (36 - len(str(port))) }║\033[0m')
    print('\033[92m╠══════════════════════════════════════════════════════════╣\033[0m')
    print('\033[92m║  \033[93m🔑 Senha: mayara123\033[92m                                          ║\033[0m')
    print('\033[92m╚══════════════════════════════════════════════════════════╝\033[0m')
    print()
    
    app.run(host='0.0.0.0', port=port, debug=False)
