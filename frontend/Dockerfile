FROM node:20-slim AS build

WORKDIR /build

COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM python:3.12-slim

WORKDIR /app

COPY --from=build /build/dist ./dist
COPY config.js ./dist/config.js
COPY server.py .

EXPOSE 8080

CMD ["python3", "server.py"]
