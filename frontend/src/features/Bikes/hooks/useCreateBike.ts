import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { createBike } from '../api';
import bikesApiClient from '../../../services/bikesApiClient';
import type { BikePayload } from '../types';
import type { ApiError } from '../../../types';

export default function useCreateBike() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();

  return useMutation<unknown, ApiError, BikePayload>({
    mutationFn: (payload) => createBike(bikesApiClient, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['bikes'] });
      navigate('/bikes');
    },
  });
}
