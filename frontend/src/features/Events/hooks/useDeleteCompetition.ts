import { useMutation, useQueryClient } from '@tanstack/react-query';
import { deleteCompetition } from '../api';
import eventsApiClient from '../../../services/eventsApiClient';
import type { ApiError } from '../../../types';

export default function useDeleteCompetition() {
  const queryClient = useQueryClient();

  return useMutation<unknown, ApiError, number>({
    mutationFn: (id) => deleteCompetition(eventsApiClient, id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['competitions'] });
    },
  });
}
