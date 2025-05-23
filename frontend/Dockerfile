#frontend/Dockerfile
FROM node:18-slim

WORKDIR /code

COPY package*.json ./

RUN npm install

COPY . .

EXPOSE 3000

# Use standard Next.js compiler instead of Turbopack in Docker
CMD ["npm", "run", "dev-no-turbo"]