import { useQuery } from '@tanstack/react-query';
import { fetchRoutes } from '../api';
import eventsApiClient from '../../../services/eventsApiClient';

export default function useFetchRoutes() {
  return useQuery({
    queryKey: ['routes'],
    queryFn: () => fetchRoutes(eventsApiClient),
  });
}
