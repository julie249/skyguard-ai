import Fastify from 'fastify';
import cors from '@fastify/cors';
import websocket from '@fastify/websocket';
import swagger from '@fastify/swagger';
import swaggerUi from '@fastify/swagger-ui';

import { config } from './config';
import { initDb } from './services/db.service';
import { stationRoutes } from './routes/stations.route';
import { alertRoutes } from './routes/alerts.route';
import { simulateRoutes } from './routes/simulate.route';
import { streamRoutes } from './routes/stream.route';
import { MLClientService } from './services/mlClient.service';

export async function buildServer() {
  const server = Fastify({
    logger: config.nodeEnv === 'development',
  });

  // CORS
  await server.register(cors, {
    origin: '*',
    methods: ['GET', 'POST', 'PATCH', 'PUT', 'DELETE'],
  });

  // WebSocket
  await server.register(websocket);

  // Swagger Documentation
  await server.register(swagger, {
    swagger: {
      info: {
        title: 'SkyGuard AI — Meteorological Anomaly Detection API',
        description: 'Main orchestration API and telemetry ingestion engine',
        version: '1.0.0',
      },
      host: `localhost:${config.port}`,
      schemes: ['http', 'ws'],
      consumes: ['application/json'],
      produces: ['application/json'],
    },
  });

  await server.register(swaggerUi, {
    routePrefix: '/docs',
    uiConfig: {
      docExpansion: 'list',
      deepLinking: false,
    },
  });

  // Register REST & WS Routes
  await server.register(stationRoutes);
  await server.register(alertRoutes);
  await server.register(simulateRoutes);
  await server.register(streamRoutes);

  // Health / Metrics endpoint proxy
  server.get('/metrics', async (req, reply) => {
    const mlHealth = await MLClientService.getHealth();
    return reply.send({
      backend: 'healthy',
      timestamp: new Date().toISOString(),
      mlService: mlHealth,
    });
  });

  return server;
}

async function start() {
  try {
    await initDb();
    const server = await buildServer();
    await server.listen({ port: config.port, host: config.host });
    console.log(`🚀 SkyGuard AI Backend running at http://localhost:${config.port}`);
    console.log(`📖 API Documentation available at http://localhost:${config.port}/docs`);
    console.log(`⚡ WebSocket Stream active at ws://localhost:${config.port}/ws/stream`);
  } catch (err) {
    console.error('Fatal error during backend startup:', err);
    process.exit(1);
  }
}

if (require.main === module) {
  start();
}
