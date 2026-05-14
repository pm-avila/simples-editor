# Development Setup

## Prerequisites

### Compiler (Local Dev)

For local development, you need the real SIMPLES compiler:

1. **Clone and build the compiler:**

   ```bash
   git clone https://github.com/pm-avila/simples-compiler /tmp/simples-compiler
   cd /tmp/simples-compiler
   make
   sudo cp simplesc /usr/local/bin/simplesc
   ```

   (Requires `sudo` to install to `/usr/local/bin`. Alternatively, set `SIMPLESC_BIN` environment variable to a local path.)

2. **Verify installation:**

   ```bash
   simplesc --help
   # or check existence:
   test -f /usr/local/bin/simplesc && echo "OK" || echo "NOT FOUND"
   ```

### Backend

1. **Create Python virtual environment:**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. **Install dependencies:**

   ```bash
   pip install -r backend/requirements.txt
   ```

3. **Run backend tests:**

   ```bash
   PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover tests -v
   ```

   If `/usr/local/bin/simplesc` is not available, integration tests will be skipped.

### Docker

To test the full Docker build:

```bash
docker-compose build backend
docker-compose up
```

The backend container will automatically clone and compile the real compiler during the build.
