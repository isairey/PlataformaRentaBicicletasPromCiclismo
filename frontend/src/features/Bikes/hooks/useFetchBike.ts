import { useQuery } from '@tanstack/react-query';
import { fetchBike } from '../api';
import bikesApiClient from '../../../services/bikesApiClient';

export default function useFetchBike(id: string) {
  return useQuery({
    queryKey: ['bikes', id],
    queryFn: () => fetchBike(bikesApiClient, id),
  });
}
