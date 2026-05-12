# Funciona em x86_64 (dev local) e ARM64 (Oracle Cloud Ampere A1)
FROM ubuntu:24.04

# Toolchain C + Python
RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential \
      python3 \
      python3-pip \
      ca-certificates \
      curl \
    && rm -rf /var/lib/apt/lists/*

# Compilador SIMPLES
COPY ./simples-compiler /opt/simples-compiler
RUN cd /opt/simples-compiler && make && cp simplesc /usr/local/bin/simplesc

# Backend Python
WORKDIR /app
COPY requirements.txt .
RUN pip install --break-system-packages -r requirements.txt

COPY . ./backend

EXPOSE 5000

CMD ["python3", "-m", "backend.app"]
