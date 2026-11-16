import { config } from '../config';
import { MLPredictResponse, MLPredictResponseSchema, Reading } from '../schemas/reading.schema';

export class MLClientService {
  private static baseUrl = config.mlServiceUrl;

  /**
   * Calls internal ML microservice POST /predict with timeout, retry-once,
   * and graceful degradation if ml-service is unreachable.
   */
  public static async predict(reading: Reading, neighborReadings?: any[]): Promise<MLPredictResponse | null> {
    const payload = {
      station_id: reading.station_id,
      timestamp: reading.timestamp,
      temperature_c: reading.temperature_c,
      pressure_hpa: reading.pressure_hpa,
      humidity_pct: reading.humidity_pct,
      neighbor_readings: neighborReadings,
    };

    const attemptFetch = async () => {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 2500);

      try {
        const response = await fetch(`${this.baseUrl}/predict`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
          signal: controller.signal,
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
          throw new Error(`ML Service responded with HTTP ${response.status}`);
        }

        const rawJson = await response.json();
        // Strict Zod schema validation
        const parsed = MLPredictResponseSchema.safeParse(rawJson);
        if (!parsed.success) {
          console.warn('[MLClient] Validation failed on ML response:', parsed.error);
          return null;
        }
        return parsed.data;
      } catch (err: any) {
        clearTimeout(timeoutId);
        throw err;
      }
    };

    try {
      return await attemptFetch();
    } catch (firstErr) {
      // Retry once on failure
      try {
        return await attemptFetch();
      } catch (retryErr: any) {
        // Graceful degradation: log error and return null (unscored)
        console.warn(`[MLClient] ML Service unreachable at ${this.baseUrl}: ${retryErr.message}. Marking reading unscored.`);
        return null;
      }
    }
  }

  public static async getHealth(): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/health`, { method: 'GET' });
      return await response.json();
    } catch (err: any) {
      return { status: 'unreachable', error: err.message };
    }
  }
}
