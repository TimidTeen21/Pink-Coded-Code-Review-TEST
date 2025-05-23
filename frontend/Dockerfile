#frontend/Dockerfile
FROM node:18-slim

# Install curl for health checks
RUN apt-get update && apt-get install -y curl

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

EXPOSE 3000

ENV NODE_ENV=development

# Use standard Next.js compiler instead of Turbopack in Docker
CMD ["npm", "run", "dev"]