import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { updateRoute } from '../api';
import eventsApiClient from '../../../services/eventsApiClient';
import type { RoutePayload } from '../types';
import type { ApiError } from '../../../types';

export default function useUpdateRoute(id: number) {
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  return useMutation<unknown, ApiError, RoutePayload>({
    mutationFn: (payload) => updateRoute(eventsApiClient, id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['routes'] });
      navigate('/routes');
    },
  });
}
