import { Card } from '../ui/Card';
import type { AccuracyMetrics as AccuracyMetricsType } from '@/types/prediction';

interface AccuracyMetricsProps {
  data: AccuracyMetricsType;
}

export const AccuracyMetrics = ({ data }: AccuracyMetricsProps) => {
  const accuracyPercent = (data.accuracy_rate * 100).toFixed(1);
  const recent30dPercent = (data.recent_30d_accuracy * 100).toFixed(1);
  const hasData = data.total_predictions > 0;

  const getAccuracyColor = (rate: number) => {
    if (rate >= 0.6) return 'text-green-600';
    if (rate >= 0.5) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getProgressBarColor = (rate: number) => {
    if (rate >= 0.6) return 'bg-green-500';
    if (rate >= 0.5) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  if (!hasData) {
    return (
      <Card>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">prediction accuracy</h2>
        <div className="text-center py-8">
          <p className="text-gray-500 mb-2">no verified predictions yet</p>
          <p className="text-sm text-gray-400">
            accuracy tracking starts after predictions are verified against actual market data
          </p>
        </div>
      </Card>
    );
  }

  return (
    <Card>
      <h2 className="text-2xl font-bold text-gray-900 mb-6">prediction accuracy</h2>

      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <span className="text-lg font-medium text-gray-700">overall accuracy</span>
          <span className={`text-2xl font-bold ${getAccuracyColor(data.accuracy_rate)}`}>
            {accuracyPercent}%
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3">
          <div
            className={`h-3 rounded-full ${getProgressBarColor(data.accuracy_rate)}`}
            style={{ width: `${accuracyPercent}%` }}
          ></div>
        </div>
        <div className="text-sm text-gray-500 mt-1">
          {data.correct_predictions} out of {data.total_predictions} predictions correct
        </div>
      </div>

      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-3">by confidence level</h3>
        <div className="space-y-3">
          {(['high', 'medium', 'low'] as const).map(level => {
            const levelData = data.by_confidence[level];
            const levelPercent = (levelData.rate * 100).toFixed(1);

            return (
              <div key={level} className="border-b pb-3 last:border-0">
                <div className="flex items-center justify-between mb-1">
                  <span className="font-medium capitalize text-gray-700">{level}</span>
                  <span className={`font-semibold ${getAccuracyColor(levelData.rate)}`}>
                    {levelPercent}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${getProgressBarColor(levelData.rate)}`}
                    style={{ width: `${levelPercent}%` }}
                  ></div>
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  {levelData.correct}/{levelData.total} correct
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div className="mb-6 border-t pt-4">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-gray-700">recent 30-day accuracy</span>
          <span className={`text-xl font-bold ${getAccuracyColor(data.recent_30d_accuracy)}`}>
            {recent30dPercent}%
          </span>
        </div>
      </div>

      <div className="border-t pt-4">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-gray-700">current streak</span>
          <span className="text-xl font-bold text-primary-600">
            {data.current_streak} {data.current_streak === 1 ? 'prediction' : 'predictions'}
          </span>
        </div>
        <div className="flex mt-2">
          {Array.from({ length: Math.min(data.current_streak, 10) }).map((_, i) => (
            <span key={i} className="text-green-500 mr-1">✓</span>
          ))}
          {data.current_streak > 10 && (
            <span className="text-gray-500 text-sm">+{data.current_streak - 10} more</span>
          )}
        </div>
      </div>
    </Card>
  );
};
