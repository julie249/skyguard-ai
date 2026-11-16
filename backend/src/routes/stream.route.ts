import { FastifyInstance } from 'fastify';
import { StreamSimulatorService } from '../services/streamSimulator.service';

export async function streamRoutes(server: FastifyInstance) {
  server.get<{
    Querystring: { stationId?: string };
  }>('/ws/stream', { websocket: true }, (connection: any, req) => {
    const { stationId } = req.query;
    const socket = connection.socket || connection;
    StreamSimulatorService.addSubscriber(socket, stationId);
  });
}
