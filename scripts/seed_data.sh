#!/bin/bash
set -e

echo "=========================================================="
echo "SkyGuard AI — Database Seeding & Synthetic Telemetry"
echo "=========================================================="

cd "$(dirname "$0")/../backend"

echo "Initializing database schema via Prisma..."
npx prisma generate --schema=src/prisma/schema.prisma
npx prisma db push --schema=src/prisma/schema.prisma

echo "Seeding initial stations and historical AWS telemetry..."
node -e "
const { initDb, prisma } = require('./dist/services/db.service');
initDb().then(async () => {
  console.log('Database successfully seeded with 6 North India AWS stations.');
  await prisma.\$disconnect();
});
"
