# Use a imagem oficial do Python 3.10 como base
FROM python:3.10-slim

# Defina o diretório de trabalho como /app
WORKDIR /app

# Copie o arquivo de requisitos para o diretório de trabalho
COPY requirements.txt .

# Instale as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Copie o seu arquivo Python para o diretório de trabalho
COPY . .

# Comando padrão para executar seu arquivo Python quando o contêiner for iniciado
CMD ["python", "main.py"]

#Execute os seguintes comandos em ordem:
#docker build -t porttaggerdante .
#docker run -v "caminho pro arquivo de saída:/app/output" porttaggerdante