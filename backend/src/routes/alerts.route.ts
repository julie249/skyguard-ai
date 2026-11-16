import { FastifyInstance } from 'fastify';
import { prisma } from '../services/db.service';

export async function alertRoutes(server: FastifyInstance) {
  server.get<{
    Querystring: { stationId?: string; status?: string; limit?: string };
  }>('/alerts', async (request, reply) => {
    const { stationId, status, limit } = request.query;

    const whereClause: any = {};
    if (stationId) whereClause.stationId = stationId;
    if (status) whereClause.status = status;

    const alerts = await prisma.alert.findMany({
      where: whereClause,
      orderBy: { timestamp: 'desc' },
      take: limit ? parseInt(limit, 10) : 50,
      include: { station: true },
    });

    const parsedAlerts = alerts.map((a) => ({
      ...a,
      triggeringFeatures: JSON.parse(a.triggeringFeatures),
      explanation: JSON.parse(a.explanation),
      spatialSupport: a.spatialSupport ? JSON.parse(a.spatialSupport) : null,
    }));

    return reply.send(parsedAlerts);
  });

  server.patch<{
    Params: { alertId: string };
    Body: { status: 'open' | 'acknowledged' | 'resolved' };
  }>('/alerts/:alertId', async (request, reply) => {
    const { alertId } = request.params;
    const { status } = request.body;

    const updated = await prisma.alert.update({
      where: { alertId },
      data: { status },
    });

    return reply.send(updated);
  });
}
