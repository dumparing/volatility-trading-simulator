import { useQuery } from '@tanstack/react-query';
import { predictionService } from '@/services/api';

export const useLatestPrediction = () => {
  return useQuery({
    queryKey: ['prediction', 'latest'],
    queryFn: predictionService.getLatest,
    staleTime: 1000 * 60 * 60,
    refetchOnWindowFocus: false,
  });
};
