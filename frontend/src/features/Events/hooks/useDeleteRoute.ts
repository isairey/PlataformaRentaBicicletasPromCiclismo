import { useMutation, useQueryClient } from '@tanstack/react-query';
import { deleteRoute } from '../api';
import eventsApiClient from '../../../services/eventsApiClient';
import type { ApiError } from '../../../types';

export default function useDeleteRoute() {
  const queryClient = useQueryClient();

  return useMutation<unknown, ApiError, number>({
    mutationFn: (id) => deleteRoute(eventsApiClient, id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['routes'] });
    },
  });
}
