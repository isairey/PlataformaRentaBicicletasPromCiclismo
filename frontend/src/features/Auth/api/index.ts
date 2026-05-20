import type { AxiosInstance } from 'axios';
import type { RegisterPayload, RegisterResponse, LoginPayload, LoginResponse } from '../types';
import type { ApiError } from '../../../types';
import { AxiosError } from 'axios';

export async function register(
  api: AxiosInstance,
  payload: RegisterPayload,
): Promise<RegisterResponse> {
  try {
    const { data } = await api.post<RegisterResponse>('auth/register', payload);
    return data;
  } catch (err) {
    if (err instanceof AxiosError && err.response?.data) {
      throw err.response.data as ApiError;
    }
    throw err;
  }
}

export async function login(
  api: AxiosInstance,
  payload: LoginPayload,
): Promise<LoginResponse> {
  try {
    const { data } = await api.post<LoginResponse>('auth/login', payload);
    return data;
  } catch (err) {
    if (err instanceof AxiosError && err.response?.data) {
      throw err.response.data as ApiError;
    }
    throw err;
  }
}
