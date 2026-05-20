import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { updateBike } from '../api';
import bikesApiClient from '../../../services/bikesApiClient';
import type { BikePayload } from '../types';
import type { ApiError } from '../../../types';

export default function useUpdateBike(id: string) {
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  return useMutation<unknown, ApiError, BikePayload>({
    mutationFn: (payload) => updateBike(bikesApiClient, id, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['bikes'] });
      navigate('/bikes');
    },
  });
}
