FROM node:21.7.1-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install --legacy-peer-deps
COPY . ./
RUN npm run build

FROM nginx:1.19.3
COPY --from=builder /app/build /usr/share/nginx/html
COPY infra/nginx.conf /etc/nginx/conf.d/default.conf

