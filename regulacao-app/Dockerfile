# =============================================================================
# DOCKERFILE - Frontend React/Expo Web
# =============================================================================

# Stage 1: Build
FROM node:18-alpine AS builder

WORKDIR /app

# Copiar package files
COPY package*.json ./

# Instalar dependências
RUN npm ci --legacy-peer-deps

# Copiar código fonte
COPY . .

# Build para web
RUN npx expo export --platform web

# Stage 2: Serve
FROM nginx:alpine

# Copiar build para nginx
COPY --from=builder /app/dist /usr/share/nginx/html

# Configuração nginx para SPA
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
