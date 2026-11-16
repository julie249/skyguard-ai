import { PrismaClient } from '@prisma/client';

export const prisma = new PrismaClient();

export async function initDb() {
  // Ensure default stations are seeded if table is empty
  const count = await prisma.station.count();
  if (count === 0) {
    const defaultStations = [
      { stationId: 'AWS001', name: 'New Delhi Ridge', lat: 28.6139, lon: 77.209, elevation: 216.0, region: 'North India' },
      { stationId: 'AWS002', name: 'Palam Airport', lat: 28.5665, lon: 77.1031, elevation: 237.0, region: 'North India' },
      { stationId: 'AWS003', name: 'Noida Sector 62', lat: 28.628, lon: 77.3649, elevation: 200.0, region: 'North India' },
      { stationId: 'AWS004', name: 'Gurugram CyberCity', lat: 28.4949, lon: 77.0895, elevation: 225.0, region: 'North India' },
      { stationId: 'AWS005', name: 'Faridabad Central', lat: 28.4089, lon: 77.3178, elevation: 206.0, region: 'North India' },
      { stationId: 'AWS006', name: 'Ghaziabad Hindon', lat: 28.7032, lon: 77.4378, elevation: 212.0, region: 'North India' },
    ];

    for (const st of defaultStations) {
      await prisma.station.create({ data: st });
    }
  }
}
