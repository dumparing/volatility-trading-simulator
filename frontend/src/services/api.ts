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

export const predictionService = {
  getLatest: () =>
    api.get<Prediction>('/predictions/latest').then(res => res.data),

  getAll: (limit = 90) =>
    api.get<Prediction[]>(`/predictions/all?limit=${limit}`).then(res => res.data),
};

export const analyticsService = {
  getAccuracy: () =>
    api.get<AccuracyMetrics>('/analytics/accuracy').then(res => res.data),
};

export default api;
