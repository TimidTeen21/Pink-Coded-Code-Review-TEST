FROM node:18-slim

WORKDIR /code

COPY package*.json ./

RUN npm install

COPY . .

EXPOSE 3000

CMD ["sh", "-c", "trap 'exit 0' SIGTERM; npm run dev & wait"]