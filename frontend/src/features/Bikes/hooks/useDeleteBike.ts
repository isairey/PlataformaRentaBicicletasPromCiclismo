import { useMutation, useQueryClient } from '@tanstack/react-query';
import { deleteBike } from '../api';
import bikesApiClient from '../../../services/bikesApiClient';

export default function useDeleteBike() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => deleteBike(bikesApiClient, id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['bikes'] });
    },
  });
}
