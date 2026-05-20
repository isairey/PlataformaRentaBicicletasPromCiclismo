import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { updateCompetition } from '../api';
import eventsApiClient from '../../../services/eventsApiClient';
import type { CompetitionPayload } from '../types';
import type { ApiError } from '../../../types';

export default function useUpdateCompetition(id: number) {
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  return useMutation<unknown, ApiError, CompetitionPayload>({
    mutationFn: (payload) => updateCompetition(eventsApiClient, id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['competitions'] });
      navigate('/competitions');
    },
  });
}
