import { buildServer } from '../src/server';
import { initDb, prisma } from '../src/services/db.service';
import { FastifyInstance } from 'fastify';

describe('SkyGuard AI Backend API Routes', () => {
  let server: FastifyInstance;

  beforeAll(async () => {
    await initDb();
    server = await buildServer();
    await server.ready();
  });

  afterAll(async () => {
    await server.close();
    await prisma.$disconnect();
  });

  test('GET /stations returns list of stations with health statuses', async () => {
    const res = await server.inject({
      method: 'GET',
      url: '/stations',
    });

    expect(res.statusCode).toBe(200);
    const stations = JSON.parse(res.payload);
    expect(Array.isArray(stations)).toBe(true);
    expect(stations.length).toBeGreaterThan(0);
    expect(stations[0]).toHaveProperty('stationId');
    expect(stations[0]).toHaveProperty('healthStatus');
  });

  test('POST /simulate/inject stores reading and returns simulated result', async () => {
    const res = await server.inject({
      method: 'POST',
      url: '/simulate/inject',
      payload: {
        stationId: 'AWS001',
        temperatureC: 55.0,
        pressureHpa: 1012.0,
        humidityPct: 20.0,
        anomalyType: 'spike',
      },
    });

    expect(res.statusCode).toBe(201);
    const body = JSON.parse(res.payload);
    expect(body).toHaveProperty('message');
    expect(body.result.reading.temperatureC).toBe(55.0);
  });

  test('GET /alerts retrieves alerts list', async () => {
    const res = await server.inject({
      method: 'GET',
      url: '/alerts',
    });

    expect(res.statusCode).toBe(200);
    const alerts = JSON.parse(res.payload);
    expect(Array.isArray(alerts)).toBe(true);
  });

  test('GET /metrics returns backend status and proxied ML status', async () => {
    const res = await server.inject({
      method: 'GET',
      url: '/metrics',
    });

    expect(res.statusCode).toBe(200);
    const metrics = JSON.parse(res.payload);
    expect(metrics.backend).toBe('healthy');
  });
});
