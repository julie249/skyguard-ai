import { WebSocket } from 'ws';
import { prisma } from './db.service';
import { MLClientService } from './mlClient.service';
import { AlertService } from './alert.service';
import { Reading } from '../schemas/reading.schema';

export class StreamSimulatorService {
  private static subscribers: Set<{ ws: WebSocket; stationId?: string }> = new Set();
  private static intervalHandle: NodeJS.Timeout | null = null;
  private static isRunning = false;

  public static addSubscriber(ws: WebSocket, stationId?: string) {
    const sub = { ws, stationId };
    this.subscribers.add(sub);

    ws.on('close', () => {
      this.subscribers.delete(sub);
    });
  }

  public static broadcast(payload: any, stationId: string) {
    const message = JSON.stringify(payload);
    for (const sub of this.subscribers) {
      if (sub.ws.readyState === WebSocket.OPEN) {
        if (!sub.stationId || sub.stationId === stationId) {
          sub.ws.send(message);
        }
      }
    }
  }

  public static async processIncomingReading(reading: Reading): Promise<any> {
    // 1. Store reading in DB
    const savedReading = await prisma.reading.create({
      data: {
        stationId: reading.station_id,
        timestamp: new Date(reading.timestamp),
        temperatureC: reading.temperature_c,
        pressureHpa: reading.pressure_hpa,
        humidityPct: reading.humidity_pct,
      },
    });

    // 2. Score via ML Microservice
    const mlResult = await MLClientService.predict(reading);

    let createdAlert = null;
    if (mlResult && mlResult.is_anomaly) {
      createdAlert = await prisma.alert.create({
        data: {
          stationId: reading.station_id,
          timestamp: new Date(reading.timestamp),
          confidence: mlResult.confidence,
          rootCause: mlResult.root_cause,
          triggeringFeatures: JSON.stringify(mlResult.triggering_features),
          explanation: JSON.stringify(mlResult.explanation),
          spatialSupport: mlResult.spatial_support ? JSON.stringify(mlResult.spatial_support) : null,
          suggestedCorrection: mlResult.suggested_correction || null,
          status: 'open',
        },
      });

      // Dispatch alert notification
      await AlertService.dispatchAlert({
        stationId: reading.station_id,
        timestamp: new Date(reading.timestamp),
        confidence: mlResult.confidence,
        rootCause: mlResult.root_cause,
        triggeringFeatures: mlResult.triggering_features,
        explanationSummary: mlResult.explanation.summary,
      });
    }

    const streamMessage = {
      reading: savedReading,
      alert: createdAlert,
      mlScored: mlResult !== null,
    };

    this.broadcast(streamMessage, reading.station_id);
    return streamMessage;
  }
}
