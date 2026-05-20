import type { AxiosInstance } from "axios";
import { AxiosError } from "axios";
import type { Rental, CreateRentalPayload } from "../types";
import type { ApiError } from "../../../types";

export async function fetchUserRentals(
  api: AxiosInstance,
  userId: string,
): Promise<Rental[]> {
  const { data } = await api.get<Rental[]>(`rental/user/${userId}`);
  return data;
}

export async function createRental(
  api: AxiosInstance,
  payload: CreateRentalPayload,
): Promise<Rental> {
  try {
    const { data } = await api.post<Rental>("rental", payload);
    return data;
  } catch (err) {
    if (err instanceof AxiosError && err.response?.data) {
      throw err.response.data as ApiError;
    }
    throw err;
  }
}

export async function returnRental(
  api: AxiosInstance,
  rentalId: string,
): Promise<Rental> {
  try {
    const { data } = await api.patch<Rental>(`rental/${rentalId}/return`, {});
    return data;
  } catch (err) {
    if (err instanceof AxiosError && err.response?.data) {
      throw err.response.data as ApiError;
    }
    throw err;
  }
}
