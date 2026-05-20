import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { createCompetition } from '../api';
import eventsApiClient from '../../../services/eventsApiClient';
import type { CompetitionPayload } from '../types';
import type { ApiError } from '../../../types';

export default function useCreateCompetition() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  return useMutation<unknown, ApiError, CompetitionPayload>({
    mutationFn: (payload) => createCompetition(eventsApiClient, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['competitions'] });
      navigate('/competitions');
    },
  });
}
