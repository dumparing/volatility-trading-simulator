import { useQuery } from '@tanstack/react-query';
import { analyticsService } from '@/services/api';

export const useAccuracyMetrics = () => {
  return useQuery({
    queryKey: ['analytics', 'accuracy'],
    queryFn: analyticsService.getAccuracy,
    staleTime: 1000 * 60 * 60 * 24,
    refetchOnWindowFocus: false,
    retry: 1,
  });
};
