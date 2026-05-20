import { useQuery } from '@tanstack/react-query';
import mapApiClient from '../../../../../services/mapApiClient';
import { fetchAvailableBikes } from '../api';
import type { BikeLocation } from '../types';

export default function useFetchAvailableBikes() {
  return useQuery<BikeLocation[]>({
    queryKey: ['availableBikes'],
    queryFn: () => fetchAvailableBikes(mapApiClient),
  });
}
