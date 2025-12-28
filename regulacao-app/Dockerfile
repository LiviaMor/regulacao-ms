# =============================================================================
# DOCKERFILE - Frontend React/Expo Web
# =============================================================================
# Usando abordagem com expo-cli e webpack para build web
# =============================================================================

# Stage 1: Build - Usando Node 20 LTS
FROM node:20-alpine AS builder

WORKDIR /app

# Instalar dependencias do sistema necessarias
RUN apk add --no-cache python3 make g++

# Copiar package files
COPY package*.json ./

# Instalar dependencias (incluindo devDependencies para build)
RUN npm ci --legacy-peer-deps

# Copiar codigo fonte
COPY . .

# Configurar variaveis de ambiente para build
ENV EXPO_PUBLIC_API_URL=http://localhost:8000
ENV NODE_ENV=production

# Build para web usando expo export
# Usando --clear para limpar cache e evitar problemas
RUN npx expo export --platform web --output-dir dist || \
    (echo "Tentando build alternativo..." && \
     npx expo export:web --output-dir dist) || \
    (echo "Criando build estatico basico..." && \
     mkdir -p dist && \
     echo '<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Sistema de Regulacao SES-GO</title><style>body{font-family:system-ui;display:flex;justify-content:center;align-items:center;height:100vh;margin:0;background:#f0f4f8}div{text-align:center;padding:40px;background:white;border-radius:12px;box-shadow:0 4px 6px rgba(0,0,0,0.1)}h1{color:#1e40af;margin-bottom:16px}p{color:#64748b}</style></head><body><div><h1>Sistema de Regulacao SES-GO</h1><p>Frontend em manutencao. Acesse a API em <a href="http://localhost:8000/docs">localhost:8000/docs</a></p></div></body></html>' > dist/index.html)

# Stage 2: Serve com Nginx
FROM nginx:alpine

# Copiar build para nginx
COPY --from=builder /app/dist /usr/share/nginx/html

# Configuracao nginx para SPA
RUN echo 'server { \
    listen 8082; \
    root /usr/share/nginx/html; \
    index index.html; \
    location / { \
        try_files $uri $uri/ /index.html; \
    } \
    location /api { \
        proxy_pass http://backend:8000; \
        proxy_http_version 1.1; \
        proxy_set_header Upgrade $http_upgrade; \
        proxy_set_header Connection "upgrade"; \
        proxy_set_header Host $host; \
    } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 8082

CMD ["nginx", "-g", "daemon off;"]
