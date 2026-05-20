import { useQuery } from '@tanstack/react-query';
import { fetchEvents } from '../api';
import eventsApiClient from '../../../services/eventsApiClient';

export default function useFetchEvents() {
  return useQuery({
    queryKey: ['events'],
    queryFn: () => fetchEvents(eventsApiClient),
  });
}
