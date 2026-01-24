import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';
import type { Prediction } from '@/types/prediction';
import { format } from 'date-fns';

interface LatestPredictionCardProps {
  data: Prediction;
}

export const LatestPredictionCard = ({ data }: LatestPredictionCardProps) => {
  const isIncrease = data.prediction === 1;
  const confidencePercent = (data.confidence_score * 100).toFixed(1);

  return (
    <Card className="max-w-4xl mx-auto">
      <div className="space-y-6">
        <h2 className="text-2xl font-bold text-gray-900">latest prediction</h2>

        <div className="flex items-center space-x-4">
          <div className={`text-6xl font-bold ${isIncrease ? 'text-success-600' : 'text-danger-600'}`}>
            {isIncrease ? '↗' : '↘'}
          </div>
          <div>
            <div className={`text-4xl font-bold ${isIncrease ? 'text-success-600' : 'text-danger-600'}`}>
              {data.prediction_text}
            </div>
          </div>
        </div>

        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-lg font-medium text-gray-700">confidence</span>
            <Badge level={data.confidence_level}>
              {data.confidence_level.toUpperCase()} ({confidencePercent}%)
            </Badge>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-4">
            <div
              className={`h-4 rounded-full transition-all ${
                data.confidence_level === 'high' ? 'bg-green-500' :
                data.confidence_level === 'medium' ? 'bg-yellow-500' :
                'bg-red-500'
              }`}
              style={{ width: `${confidencePercent}%` }}
            ></div>
          </div>
        </div>

        <div className="flex items-center justify-between text-sm text-gray-500 border-t pt-4">
          <div>
            <span className="font-medium">date:</span>{' '}
            {format(new Date(data.date + 'T12:00:00'), 'MMMM d, yyyy')}
          </div>
          <div>
            <span className="font-medium">predicted at:</span>{' '}
            {new Date(data.timestamp).toLocaleString('en-US', {
              hour: 'numeric',
              minute: '2-digit',
              hour12: true,
              timeZone: 'America/Denver'
            })} MT
          </div>
        </div>

      </div>
    </Card>
  );
};
