import { useMutation, useQueryClient } from '@tanstack/react-query';
import { deleteEvent } from '../api';
import eventsApiClient from '../../../services/eventsApiClient';
import type { ApiError } from '../../../types';

export default function useDeleteEvent() {
  const queryClient = useQueryClient();

  return useMutation<unknown, ApiError, number>({
    mutationFn: (id) => deleteEvent(eventsApiClient, id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['events'] });
    },
  });
}
