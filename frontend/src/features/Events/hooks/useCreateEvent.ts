import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { createEvent } from '../api';
import eventsApiClient from '../../../services/eventsApiClient';
import type { EventPayload } from '../types';
import type { ApiError } from '../../../types';

export default function useCreateEvent() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  return useMutation<unknown, ApiError, EventPayload>({
    mutationFn: (payload) => createEvent(eventsApiClient, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['events'] });
      navigate('/events');
    },
  });
}
