import socket
import time
import sys

# Lista de tuplas: (caminho_no_seu_pc, nome_no_esp32)
arquivos = [
    ('boot.py', 'boot.py'),
    ('main.py', 'main.py'),
    ('lib/ssd1306.py', 'ssd1306.py'),
    ('lib/umqttsimple.py', 'umqttsimple.py'),
    ('dotenv.py', 'dotenv.py'),
    ('.env', '.env')
]

def enviar_arquivo(caminho_local, nome_esp, porta=4001):
    try:
        with open(caminho_local, "r", encoding="utf-8") as f:
            linhas = f.readlines()
    except FileNotFoundError:
        print(f"⚠️  Arquivo {caminho_local} não encontrado. Pulando...")
        return

    print(f"Enviando {caminho_local}...")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        s.connect(('127.0.0.1', porta))
    except ConnectionRefusedError:
        print("❌ Erro: O simulador do Wokwi não está rodando. Dê Play no VS Code primeiro!")
        sys.exit(1)

    time.sleep(1) # Aguarda o prompt
    s.send(b'\r\x03\x03') # Ctrl+C duplo para garantir que o terminal está livre
    time.sleep(0.5)
    
    # Abre o arquivo para escrita
    s.send(f"f = open('{nome_esp}', 'w')\r\n".encode('utf-8'))
    time.sleep(0.2)
    
    for linha in linhas:
        linha_limpa = linha.replace('\\', '\\\\').replace('"', '\\"').replace('\r', '').replace('\n', '')
        s.send(f'f.write("{linha_limpa}\\n")\r\n'.encode('utf-8'))
        time.sleep(0.05) 
        
    s.send(b"f.close()\r\n")
    time.sleep(0.2)
    s.close()
    print(f"✓ {nome_esp} OK!")

print("Iniciando deploy automático para o Wokwi...")
for caminho_local, nome_esp in arquivos:
    enviar_arquivo(caminho_local, nome_esp)
    time.sleep(0.5)

print("\nFazendo Soft Reset no ESP32 para iniciar o código...")
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('127.0.0.1', 4001))
    s.send(b'\r\x04') # O caractere \x04 simula o Ctrl+D (Soft Reset)
    s.close()
except Exception:
    pass

print("Deploy concluído! Acompanhe o terminal do Wokwi.")