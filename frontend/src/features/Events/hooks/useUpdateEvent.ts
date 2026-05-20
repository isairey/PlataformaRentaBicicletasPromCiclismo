import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { updateEvent } from '../api';
import eventsApiClient from '../../../services/eventsApiClient';
import type { EventPayload } from '../types';
import type { ApiError } from '../../../types';

export default function useUpdateEvent(id: number) {
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  return useMutation<unknown, ApiError, EventPayload>({
    mutationFn: (payload) => updateEvent(eventsApiClient, id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['events'] });
      navigate('/events');
    },
  });
}
