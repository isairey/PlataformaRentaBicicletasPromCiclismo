import { useMutation } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { login } from '../api';
import authApiClient from '../../../services/authApiClient';
import { useAuth } from '../../../services/useAuth';
import type { LoginPayload, LoginResponse } from '../types';
import type { ApiError } from '../../../types';

export default function useLogin() {
  const navigate = useNavigate();
  const { login: authLogin } = useAuth();

  return useMutation<LoginResponse, ApiError, LoginPayload>({
    mutationFn: (payload) => login(authApiClient, payload),
    onSuccess: (data) => {
      authLogin({
        user: { uid: data.localId, email: data.email },
        idToken: data.idToken,
        refreshToken: data.refreshToken,
      });
      navigate('/');
    },
  });
}
