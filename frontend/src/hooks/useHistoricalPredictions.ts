import { useQuery } from '@tanstack/react-query';
import { predictionService } from '@/services/api';

export const useHistoricalPredictions = (days = 90) => {
  return useQuery({
    queryKey: ['predictions', 'historical', days],
    queryFn: () => predictionService.getAll(days),
    staleTime: 1000 * 60 * 60 * 24,
    refetchOnWindowFocus: false,
  });
};
