# ── SkyGuard AI · Backend (Node 20 + Prisma + SQLite) ────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
COPY src/prisma ./src/prisma/

# Install ALL deps (including devDeps for tsc)
RUN npm ci

COPY . .

# Generate Prisma client then compile TypeScript
RUN npx prisma generate --schema=src/prisma/schema.prisma
RUN npm run build

# ── Runtime stage ─────────────────────────────────────────────────────────────
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --omit=dev

# Copy compiled output and Prisma artefacts from builder
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules/.prisma ./node_modules/.prisma
COPY --from=builder /app/node_modules/@prisma ./node_modules/@prisma
COPY src/prisma ./src/prisma/
COPY seed_demo.js ./seed_demo.js
COPY docker-entrypoint.sh ./docker-entrypoint.sh

RUN chmod +x docker-entrypoint.sh

EXPOSE 3000

ENV PORT=3000
ENV HOST=0.0.0.0
ENV NODE_ENV=production

HEALTHCHECK --interval=15s --timeout=5s --start-period=30s --retries=3 \
  CMD wget -qO- http://localhost:3000/metrics || exit 1

ENTRYPOINT ["./docker-entrypoint.sh"]
