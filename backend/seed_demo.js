const { prisma, initDb } = require('./dist/services/db.service');
const fs = require('fs');
const path = require('path');

async function seed() {
  await initDb();
  const csvPath = path.resolve(__dirname, '../data/synthetic/aws_synthetic_3pct.csv');
  if (!fs.existsSync(csvPath)) {
    console.error('Synthetic CSV not found at', csvPath);
    return;
  }

  const raw = fs.readFileSync(csvPath, 'utf8');
  const lines = raw.trim().split('\n').slice(1, 201); // Load 200 telemetry records

  let inserted = 0;
  for (const line of lines) {
    const parts = line.split(',');
    if (parts.length >= 5) {
      const [stId, ts, temp, pres, hum] = parts;
      await prisma.reading.create({
        data: {
          stationId: stId.trim(),
          timestamp: new Date(ts.trim()),
          temperatureC: parseFloat(temp),
          pressureHpa: parseFloat(pres),
          humidityPct: parseFloat(hum),
        },
      });
      inserted++;
    }
  }

  // Also seed 2 initial demo alerts
  await prisma.alert.create({
    data: {
      stationId: 'AWS001',
      timestamp: new Date(Date.now() - 3600000),
      confidence: 0.88,
      rootCause: 'sensor_fault',
      triggeringFeatures: JSON.stringify(['temperature_c']),
      explanation: JSON.stringify({
        feature_contributions: { temperature_c: 0.85, pressure_hpa: 0.1, humidity_pct: 0.05 },
        summary: 'Temperature C spiked +28.5°C above seasonal expectation while neighboring stations remained nominal.',
      }),
      spatialSupport: JSON.stringify({
        agreement_score: 0.0,
        agreeing_neighbors_count: 0,
        total_neighbors_evaluated: 2,
        is_corroborated: false,
        suggested_correction: 26.8,
        summary: '0/2 neighbor stations corroborate observation.',
      }),
      suggestedCorrection: 26.8,
      status: 'open',
    },
  });

  await prisma.alert.create({
    data: {
      stationId: 'AWS004',
      timestamp: new Date(Date.now() - 7200000),
      confidence: 0.94,
      rootCause: 'genuine_extreme',
      triggeringFeatures: JSON.stringify(['temperature_c', 'pressure_hpa']),
      explanation: JSON.stringify({
        feature_contributions: { temperature_c: 0.55, pressure_hpa: 0.45 },
        summary: 'Intense microburst with sudden 18 hPa pressure drop corroborated by surrounding AWS grid.',
      }),
      spatialSupport: JSON.stringify({
        agreement_score: 1.0,
        agreeing_neighbors_count: 2,
        total_neighbors_evaluated: 2,
        is_corroborated: true,
        summary: '2/2 neighbor stations observed synchronous barometric departure.',
      }),
      suggestedCorrection: null,
      status: 'acknowledged',
    },
  });

  console.log(`Successfully seeded ${inserted} historical readings and 2 realistic demo alerts.`);
  await prisma.$disconnect();
}

seed().catch(console.error);
