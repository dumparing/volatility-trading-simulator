import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { LatestPredictionCard } from './components/dashboard/LatestPredictionCard';
import { HistoricalChart } from './components/dashboard/HistoricalChart';
import { AccuracyMetrics } from './components/dashboard/AccuracyMetrics';
import { TechnicalIndicators } from './components/dashboard/TechnicalIndicators';
import { CardSkeleton } from './components/ui/LoadingSpinner';
import { useLatestPrediction } from './hooks/useLatestPrediction';
import { useHistoricalPredictions } from './hooks/useHistoricalPredictions';
import { useAccuracyMetrics } from './hooks/useAccuracyMetrics';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 1000 * 60 * 5,
    },
  },
});

function Dashboard() {
  const { data: latest, isLoading: latestLoading, error: latestError } = useLatestPrediction();
  const { data: historical, isLoading: historicalLoading } = useHistoricalPredictions(90);
  const { data: accuracy, isLoading: accuracyLoading } = useAccuracyMetrics();

  if (latestError) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">error loading predictions</h2>
          <p className="text-gray-600 mb-4">{(latestError as Error).message}</p>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
          >
            reload page
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <h1 className="text-3xl font-bold text-gray-900">volatility trading simulator</h1>
          <p className="mt-1 text-sm text-gray-600">
            ml-powered spy volatility predictions | updated daily at 5pm et
          </p>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-8">
          {latestLoading ? (
            <CardSkeleton />
          ) : latest ? (
            <LatestPredictionCard data={latest} />
          ) : (
            <div className="text-center text-gray-600">no predictions available</div>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div className="lg:col-span-2">
              {historicalLoading ? (
                <CardSkeleton />
              ) : historical && historical.length > 0 ? (
                <HistoricalChart data={historical} />
              ) : (
                <div className="text-center text-gray-600">no historical data available</div>
              )}
            </div>

            <div>
              {accuracyLoading ? (
                <CardSkeleton />
              ) : accuracy ? (
                <AccuracyMetrics data={accuracy} />
              ) : (
                <div className="text-center text-gray-600">no accuracy data available</div>
              )}
            </div>

            <div>
              {historicalLoading ? (
                <CardSkeleton />
              ) : historical && historical.length > 0 ? (
                <TechnicalIndicators data={historical} />
              ) : (
                <div className="text-center text-gray-600">no indicator data available</div>
              )}
            </div>
          </div>
        </div>
      </main>

      <footer className="bg-white border-t mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-sm text-gray-500">
            powered by xgboost | deployed on aws lambda | cost: ~$0.08/month
          </p>
        </div>
      </footer>
    </div>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Dashboard />
    </QueryClientProvider>
  );
}

export default App;
