import { z } from 'zod';

export const ReadingSchema = z.object({
  station_id: z.string(),
  timestamp: z.string(),
  temperature_c: z.number(),
  pressure_hpa: z.number(),
  humidity_pct: z.number(),
  is_anomaly: z.boolean().nullable().optional(),
  anomaly_type: z.enum(['spike', 'stuck', 'dropout', 'drift', 'noise']).nullable().optional(),
});

export type Reading = z.infer<typeof ReadingSchema>;

export const MLPredictResponseSchema = z.object({
  is_anomaly: z.boolean(),
  confidence: z.number().min(0).max(1),
  root_cause: z.string(),
  triggering_features: z.array(z.string()),
  explanation: z.object({
    feature_contributions: z.record(z.number()),
    summary: z.string(),
  }),
  spatial_support: z
    .object({
      agreement_score: z.number().optional(),
      agreeing_neighbors_count: z.number().optional(),
      is_corroborated: z.boolean().optional(),
      suggested_correction: z.number().nullable().optional(),
      summary: z.string().optional(),
    })
    .nullable()
    .optional(),
  suggested_correction: z.number().nullable().optional(),
  latency_ms: z.number().optional(),
});

export type MLPredictResponse = z.infer<typeof MLPredictResponseSchema>;

export const AlertSchema = z.object({
  alert_id: z.string().uuid(),
  station_id: z.string(),
  timestamp: z.string(),
  detected_at: z.string(),
  confidence: z.number(),
  root_cause: z.string(),
  triggering_features: z.array(z.string()),
  explanation: z.any(),
  spatial_support: z.any().nullable().optional(),
  suggested_correction: z.number().nullable().optional(),
  status: z.enum(['open', 'acknowledged', 'resolved']),
});

export type Alert = z.infer<typeof AlertSchema>;
