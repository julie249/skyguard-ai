import { FastifyInstance } from 'fastify';
import { prisma } from '../services/db.service';

export async function stationRoutes(server: FastifyInstance) {
  server.get('/stations', async (request, reply) => {
    const stations = await prisma.station.findMany({
      include: {
        alerts: {
          where: { status: 'open' },
          orderBy: { timestamp: 'desc' },
          take: 1,
        },
      },
    });

    const stationsWithHealth = stations.map((st) => {
      const hasActiveAlert = st.alerts.length > 0;
      return {
        stationId: st.stationId,
        name: st.name,
        lat: st.lat,
        lon: st.lon,
        elevation: st.elevation,
        region: st.region,
        healthStatus: hasActiveAlert ? 'warning' : 'healthy',
        activeAlert: st.alerts[0] || null,
      };
    });

    return reply.send(stationsWithHealth);
  });

  server.get<{
    Params: { id: string };
    Querystring: { from?: string; to?: string; limit?: string };
  }>('/stations/:id/readings', async (request, reply) => {
    const { id } = request.params;
    const { from, to, limit } = request.query;

    const whereClause: any = { stationId: id };
    if (from || to) {
      whereClause.timestamp = {};
      if (from) whereClause.timestamp.gte = new Date(from);
      if (to) whereClause.timestamp.lte = new Date(to);
    }

    const readings = await prisma.reading.findMany({
      where: whereClause,
      orderBy: { timestamp: 'desc' },
      take: limit ? parseInt(limit, 10) : 100,
    });

    return reply.send(readings.reverse());
  });
}
