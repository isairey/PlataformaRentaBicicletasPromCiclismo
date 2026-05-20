import type { AxiosInstance } from 'axios';
import type { BikeLocation } from '../types';

export async function fetchAvailableBikes(api: AxiosInstance): Promise<BikeLocation[]> {
  const { data } = await api.get<BikeLocation[]>('locations/available');
  return data;
}
