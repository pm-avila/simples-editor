# Funciona em x86_64 (dev local) e ARM64 (Oracle Cloud Ampere A1)
FROM ubuntu:24.04

# Toolchain cross-target i386 + Python + Git
RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential \
      nasm \
      binutils-i686-linux-gnu \
      qemu-user-static \
      python3 \
      python3-pip \
      ca-certificates \
      curl \
      git \
    && rm -rf /var/lib/apt/lists/*

# Clone and build the real SIMPLES compiler
RUN git clone https://github.com/pm-avila/simples-compiler /tmp/compiler && \
    cd /tmp/compiler && \
    make && \
    cp build/simplesc /usr/local/bin/simplesc && \
    rm -rf /tmp/compiler

# Backend Python
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --break-system-packages -r requirements.txt

COPY backend ./backend
COPY tests ./tests

EXPOSE 5000

CMD ["python3", "-m", "backend.app"]
