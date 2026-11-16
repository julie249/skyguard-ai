import { FastifyInstance } from 'fastify';
import { StreamSimulatorService } from '../services/streamSimulator.service';
import { ReadingSchema } from '../schemas/reading.schema';

export async function simulateRoutes(server: FastifyInstance) {
  server.post<{
    Body: {
      stationId?: string;
      temperatureC?: number;
      pressureHpa?: number;
      humidityPct?: number;
      anomalyType?: 'spike' | 'stuck' | 'dropout' | 'drift' | 'noise';
    };
  }>('/simulate/inject', async (request, reply) => {
    const {
      stationId = 'AWS001',
      temperatureC = 52.5, // Extreme default spike
      pressureHpa = 1008.0,
      humidityPct = 22.0,
      anomalyType = 'spike',
    } = request.body || {};

    const reading = {
      station_id: stationId,
      timestamp: new Date().toISOString(),
      temperature_c: temperatureC,
      pressure_hpa: pressureHpa,
      humidity_pct: humidityPct,
      is_anomaly: true,
      anomaly_type: anomalyType,
    };

    // Validate reading schema
    const parsed = ReadingSchema.parse(reading);

    // Process through pipeline: DB store -> ML score -> WS broadcast
    const result = await StreamSimulatorService.processIncomingReading(parsed);

    return reply.status(201).send({
      message: 'Anomaly successfully injected into stream pipeline',
      result,
    });
  });
}
