FROM python:3.10-slim

# Instala as dependências do Ubuntu: ffmpeg, jq, curl
RUN apt-get update && apt-get install -y \
    ffmpeg \
    jq \
    curl \
    && rm -rf /var/lib/apt/lists/* # Limpa o cache para manter a imagem menor

WORKDIR /
COPY requirements.txt /requirements.txt
RUN pip install -r requirements.txt
COPY rp_handler.py /

# Start the container
CMD ["python3", "-u", "rp_handler.py"]