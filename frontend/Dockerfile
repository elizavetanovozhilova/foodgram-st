# build env
FROM node:21.7.1-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install --legacy-peer-deps
COPY . ./
RUN npm install react-meta-tags --legacy-peer-deps
CMD cp -r build result_build
