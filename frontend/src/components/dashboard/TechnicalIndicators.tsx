import { Card } from '../ui/Card';
import type { Prediction } from '@/types/prediction';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { format } from 'date-fns';

interface TechnicalIndicatorsProps {
  data: Prediction[];
}

export const TechnicalIndicators = ({ data }: TechnicalIndicatorsProps) => {
  const chartData = data
    .map(pred => ({
      date: pred.date,
      volatility_20d: pred.volatility_20d * 1000,
      rsi: pred.rsi,
      bb_width: pred.bb_width * 1000,
      macd: pred.macd,
      volume_ratio: pred.volume_ratio * 10,
    }))
    .reverse();

  return (
    <Card>
      <h2 className="text-2xl font-bold text-gray-900 mb-6">technical indicators</h2>

      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="date"
            tickFormatter={(value) => format(new Date(value), 'MMM d')}
          />
          <YAxis />
          <Tooltip
            content={({ active, payload }) => {
              if (active && payload && payload.length) {
                const data = payload[0].payload;
                return (
                  <div className="bg-white p-4 border border-gray-200 rounded shadow-lg">
                    <p className="font-bold mb-2">{format(new Date(data.date), 'MMMM d, yyyy')}</p>
                    <div className="space-y-1 text-sm">
                      <p>
                        <span className="text-blue-600">●</span> volatility (20d): {(data.volatility_20d / 1000).toFixed(4)}
                      </p>
                      <p>
                        <span className="text-purple-600">●</span> rsi: {data.rsi.toFixed(2)}
                      </p>
                      <p>
                        <span className="text-orange-600">●</span> bollinger width: {(data.bb_width / 1000).toFixed(4)}
                      </p>
                      <p>
                        <span className="text-green-600">●</span> macd: {data.macd.toFixed(3)}
                      </p>
                      <p>
                        <span className="text-red-600">●</span> volume ratio: {(data.volume_ratio / 10).toFixed(2)}
                      </p>
                    </div>
                  </div>
                );
              }
              return null;
            }}
          />
          <Legend
            formatter={(value) => {
              const labels: Record<string, string> = {
                volatility_20d: 'volatility (20d)',
                rsi: 'rsi',
                bb_width: 'bollinger width',
                macd: 'macd',
                volume_ratio: 'volume ratio',
              };
              return labels[value] || value;
            }}
          />
          <Line type="monotone" dataKey="volatility_20d" stroke="#3b82f6" strokeWidth={2} dot={false} />
          <Line type="monotone" dataKey="rsi" stroke="#9333ea" strokeWidth={2} dot={false} />
          <Line type="monotone" dataKey="bb_width" stroke="#f59e0b" strokeWidth={2} dot={false} />
          <Line type="monotone" dataKey="macd" stroke="#22c55e" strokeWidth={2} dot={false} />
          <Line type="monotone" dataKey="volume_ratio" stroke="#ef4444" strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>

      <div className="mt-4 text-sm text-gray-600">
        note: values are normalized for visual comparison. hover for actual values.
      </div>
    </Card>
  );
};
