export interface Prediction {
  date: string;
  prediction: 0 | 1;
  prediction_text: string;
  confidence_score: number;
  confidence_level: 'low' | 'medium' | 'high';
  timestamp: string;
  volatility_20d: number;
  rsi: number;
  bb_width: number;
  macd: number;
  volume_ratio: number;
  actual_volatility_20d?: number;
  actual_change?: 0 | 1;
  is_correct?: boolean;
  verified_at?: string;
}

export interface AccuracyMetrics {
  total_predictions: number;
  correct_predictions: number;
  accuracy_rate: number;
  by_confidence: {
    high: { total: number; correct: number; rate: number };
    medium: { total: number; correct: number; rate: number };
    low: { total: number; correct: number; rate: number };
  };
  recent_30d_accuracy: number;
  current_streak: number;
}
