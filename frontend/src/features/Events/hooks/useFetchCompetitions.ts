import { useQuery } from '@tanstack/react-query';
import { fetchCompetitions } from '../api';
import eventsApiClient from '../../../services/eventsApiClient';

export default function useFetchCompetitions() {
  return useQuery({
    queryKey: ['competitions'],
    queryFn: () => fetchCompetitions(eventsApiClient),
  });
}
