import { useMutation, useQueryClient } from '@tanstack/react-query';
import rentalApiClient from '../../../services/rentalApiClient';
import { createRental } from '../api';
import type { Rental, CreateRentalPayload } from '../types';
import type { ApiError } from '../../../types';

export default function useCreateRental() {
  const queryClient = useQueryClient();

  return useMutation<Rental, ApiError, CreateRentalPayload>({
    mutationFn: (payload) => createRental(rentalApiClient, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['userRentals'] });
      queryClient.invalidateQueries({ queryKey: ['availableBikes'] });
    },
  });
}
