import type { AxiosInstance } from "axios";
import { AxiosError } from "axios";
import type { Bike, BikeData, BikePayload } from "../types";
import type { ApiError } from "../../../types";

export async function fetchBikes(api: AxiosInstance): Promise<BikeData> {
  const { data } = await api.get<BikeData>("bikes");
  return data;
}

export async function fetchBike(api: AxiosInstance, id: string): Promise<Bike> {
  const { data } = await api.get<Bike>(`bikes/${id}`);
  return data;
}

export async function createBike(
  api: AxiosInstance,
  payload: BikePayload,
): Promise<Bike> {
  try {
    const { data } = await api.post<Bike>("bikes", payload);
    return data;
  } catch (err) {
    if (err instanceof AxiosError && err.response?.data) {
      throw err.response.data as ApiError;
    }
    throw err;
  }
}

export async function updateBike(
  api: AxiosInstance,
  id: string,
  payload: BikePayload,
): Promise<Bike> {
  try {
    const { data } = await api.put<Bike>(`bikes/${id}`, payload);
    return data;
  } catch (err) {
    if (err instanceof AxiosError && err.response?.data) {
      throw err.response.data as ApiError;
    }
    throw err;
  }
}

export async function deleteBike(
  api: AxiosInstance,
  id: string,
): Promise<void> {
  await api.delete(`bikes/${id}`);
}
