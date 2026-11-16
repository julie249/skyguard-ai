import TelegramBot from 'node-telegram-bot-api';
import { config } from '../config';

export class AlertService {
  private static bot: TelegramBot | null = null;

  private static getBot(): TelegramBot | null {
    if (!this.bot && config.telegram.botToken) {
      try {
        this.bot = new TelegramBot(config.telegram.botToken, { polling: false });
      } catch (err) {
        console.warn('[AlertService] Failed to initialize Telegram Bot:', err);
      }
    }
    return this.bot;
  }

  public static async dispatchAlert(alert: {
    stationId: string;
    timestamp: Date;
    confidence: number;
    rootCause: string;
    triggeringFeatures: string[];
    explanationSummary: string;
  }): Promise<void> {
    if (alert.confidence < config.telegram.confidenceThreshold) {
      return;
    }

    const bot = this.getBot();
    const chatId = config.telegram.chatId;

    if (!bot || !chatId) {
      // Graceful bypass: Telegram unconfigured
      return;
    }

    const message = [
      `🚨 *SKYGUARD AI ANOMALY ALERT*`,
      `Station: \`${alert.stationId}\``,
      `Time: ${alert.timestamp.toISOString()}`,
      `Confidence: ${(alert.confidence * 100).toFixed(1)}%`,
      `Root Cause: *${alert.rootCause.toUpperCase()}*`,
      `Triggers: ${alert.triggeringFeatures.join(', ')}`,
      `Explanation: ${alert.explanationSummary}`,
    ].join('\n');

    try {
      await bot.sendMessage(chatId, message, { parse_mode: 'Markdown' });
    } catch (err: any) {
      console.warn('[AlertService] Telegram dispatch failed:', err.message);
    }
  }
}
