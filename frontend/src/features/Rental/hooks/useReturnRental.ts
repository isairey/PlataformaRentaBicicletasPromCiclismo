import { useMutation, useQueryClient } from '@tanstack/react-query';
import rentalApiClient from '../../../services/rentalApiClient';
import { returnRental } from '../api';
import type { Rental } from '../types';
import type { ApiError } from '../../../types';

export default function useReturnRental() {
  const queryClient = useQueryClient();

  return useMutation<Rental, ApiError, string>({
    mutationFn: (rentalId) => returnRental(rentalApiClient, rentalId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['userRentals'] });
      queryClient.invalidateQueries({ queryKey: ['availableBikes'] });
    },
  });
}
