import { useMutation } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { register } from '../api';
import authApiClient from '../../../services/authApiClient';
import type { RegisterPayload } from '../types';
import type { ApiError } from '../../../types';

export default function useRegister() {
  const navigate = useNavigate();

  return useMutation<unknown, ApiError, RegisterPayload>({
    mutationFn: (payload) => register(authApiClient, payload),
    onSuccess: () => {
      navigate('/login');
    },
  });
}
