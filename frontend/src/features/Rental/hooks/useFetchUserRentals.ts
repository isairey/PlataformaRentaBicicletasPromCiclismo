import { useQuery } from '@tanstack/react-query';
import rentalApiClient from '../../../services/rentalApiClient';
import { useAuth } from '../../../services/useAuth';
import { fetchUserRentals } from '../api';
import type { Rental } from '../types';

export default function useFetchUserRentals() {
  const { user } = useAuth();

  return useQuery<Rental[]>({
    queryKey: ['userRentals', user?.uid],
    queryFn: () => fetchUserRentals(rentalApiClient, user!.uid),
    enabled: !!user,
  });
}
