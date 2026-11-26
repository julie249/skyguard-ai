#!/bin/sh
# docker-entrypoint.sh — runs DB migrations then seeds (idempotent), then starts server
set -e

echo "[entrypoint] Running Prisma db push..."
npx prisma db push --schema=src/prisma/schema.prisma --accept-data-loss

# Only seed if the StationReading table is empty
ROW_COUNT=$(node -e "
const { PrismaClient } = require('@prisma/client');
const p = new PrismaClient();
p.stationReading.count().then(n => { console.log(n); p.\$disconnect(); }).catch(() => { console.log(0); p.\$disconnect(); });
")

if [ "$ROW_COUNT" -eq "0" ]; then
  echo "[entrypoint] Seeding demo data..."
  node seed_demo.js
else
  echo "[entrypoint] DB already seeded ($ROW_COUNT rows), skipping."
fi

echo "[entrypoint] Starting SkyGuard backend..."
exec node dist/server.js
