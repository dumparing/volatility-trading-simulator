import axios from 'axios';
import type { Prediction, AccuracyMetrics } from '@/types/prediction';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:3000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 429) {
      throw new Error('too many requests. please try again later');
    }
    if (error.response?.status === 404) {
      throw new Error('data not found');
    }
    if (!error.response) {
      throw new Error('network error. please check your connection');
    }
    throw error;
  }
);

function normalizePrediction(data: Record<string, unknown>): Prediction {
  const prediction = Math.round(Number(data.prediction)) as 0 | 1;
  const rawText = String(data.prediction_text || '').toLowerCase();
  const predictionText = rawText.includes('increase')
    ? 'volatility will increase'
    : 'volatility will decrease';

  return {
    date: String(data.date),
    prediction,
    prediction_text: predictionText,
    confidence_score: Number(data.confidence_score || data.confidence || 0),
    confidence_level: (data.confidence_level as 'low' | 'medium' | 'high') || 'low',
    timestamp: String(data.timestamp),
    volatility_20d: Number(data.volatility_20d || 0),
    rsi: Number(data.rsi || 0),
    bb_width: Number(data.bb_width || 0),
    macd: Number(data.macd || 0),
    volume_ratio: Number(data.volume_ratio || 0),
    actual_volatility_20d: data.actual_volatility_20d != null ? Number(data.actual_volatility_20d) : undefined,
    actual_change: data.actual_change != null ? (Math.round(Number(data.actual_change)) as 0 | 1) : undefined,
    is_correct: data.is_correct != null ? Boolean(data.is_correct) : undefined,
    verified_at: data.verified_at != null ? String(data.verified_at) : undefined,
  };
}

export const predictionService = {
  getLatest: () =>
    api.get('/predictions/latest').then(res => normalizePrediction(res.data)),

  getAll: (limit = 90) =>
    api.get(`/predictions/all?limit=${limit}`).then(res =>
      (res.data as Record<string, unknown>[]).map(normalizePrediction)
    ),
};

export const analyticsService = {
  getAccuracy: () =>
    api.get<AccuracyMetrics>('/analytics/accuracy').then(res => res.data),
};

export default api;
