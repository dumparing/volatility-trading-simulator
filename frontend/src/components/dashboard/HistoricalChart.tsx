import { Card } from '../ui/Card';
import type { Prediction } from '@/types/prediction';
import { Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Area, ComposedChart } from 'recharts';
import { format } from 'date-fns';

interface HistoricalChartProps {
  data: Prediction[];
}

export const HistoricalChart = ({ data }: HistoricalChartProps) => {
  const chartData = data
    .map(pred => ({
      date: pred.date,
      confidence: pred.confidence_score * 100,
      prediction: pred.prediction,
      predictionText: pred.prediction_text,
      level: pred.confidence_level,
    }))
    .reverse();

  return (
    <Card>
      <h2 className="text-2xl font-bold text-gray-900 mb-6">prediction history</h2>

      <ResponsiveContainer width="100%" height={400}>
        <ComposedChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="date"
            tickFormatter={(value) => format(new Date(value + 'T12:00:00'), 'MMM d')}
          />
          <YAxis
            label={{ value: 'confidence (%)', angle: -90, position: 'insideLeft' }}
            domain={[0, 100]}
          />
          <Tooltip
            content={({ active, payload }) => {
              if (active && payload && payload.length) {
                const data = payload[0].payload;
                return (
                  <div className="bg-white p-4 border border-gray-200 rounded shadow-lg">
                    <p className="font-bold">{format(new Date(data.date + 'T12:00:00'), 'MMMM d, yyyy')}</p>
                    <p className="text-sm">{data.predictionText}</p>
                    <p className="text-sm">
                      confidence: <span className="font-medium">{data.confidence.toFixed(1)}%</span>
                    </p>
                    <p className="text-sm">
                      level: <span className="font-medium capitalize">{data.level}</span>
                    </p>
                  </div>
                );
              }
              return null;
            }}
          />
          <Legend />
          <Area
            type="monotone"
            dataKey="confidence"
            fill="#3b82f6"
            fillOpacity={0.2}
            stroke="none"
          />
          <Line
            type="monotone"
            dataKey="confidence"
            stroke="#3b82f6"
            strokeWidth={2}
            dot={{ r: 3 }}
            activeDot={{ r: 6 }}
          />
        </ComposedChart>
      </ResponsiveContainer>

      <div className="mt-4 text-sm text-gray-600">
        showing last {data.length} predictions
      </div>
    </Card>
  );
};
