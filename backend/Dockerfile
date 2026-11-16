# SkyGuard AI Node.js Backend Container
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
COPY src/prisma ./src/prisma/

RUN npm install

COPY . .

RUN npx prisma generate --schema=src/prisma/schema.prisma
RUN npm run build

EXPOSE 3000

ENV PORT=3000
ENV HOST=0.0.0.0
ENV NODE_ENV=production

CMD ["npm", "start"]
