def load(filename=".env"):
    env_vars = {}
    try:
        with open(filename, 'r') as f:
            for line in f:
                # Remove espaços em branco e quebras de linha
                line = line.strip()
                # Ignora linhas vazias ou comentários
                if not line or line.startswith('#'):
                    continue
                # Divide a linha no primeiro '=' que encontrar
                if '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    except OSError:
        print(f"Aviso: Arquivo {filename} não encontrado. Usando variáveis padrão.")
    
    return env_vars