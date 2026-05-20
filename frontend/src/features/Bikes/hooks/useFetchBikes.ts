import { useQuery } from '@tanstack/react-query';
import { fetchBikes } from '../api';
import bikesApiClient from '../../../services/bikesApiClient';

export default function useFetchBikes() {
  return useQuery({
    queryKey: ['bikes'],
    queryFn: () => fetchBikes(bikesApiClient),
  });
}
