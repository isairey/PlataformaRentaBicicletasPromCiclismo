/** Coinciden con `BikeType` / `BikeState` en el MS bikes */
export const BIKE_TYPE_OPTIONS = ["Cross", "Mountain", "Street"] as const;
export type BikeTypeOption = (typeof BIKE_TYPE_OPTIONS)[number];

export const BIKE_STATE_OPTIONS = ["Free", "Rented"] as const;
export type BikeStateOption = (typeof BIKE_STATE_OPTIONS)[number];

export interface Bike {
  id: string;
  brand: string;
  type: string;
  colour: string;
  latitude?: number;
  longitude?: number;
  state?: string;
}

export interface BikePayload {
  brand: string;
  type: string;
  colour: string;
  latitude: number;
  longitude: number;
  state?: string;
}

export type BikeData = {
  bikes: Bike[];
  page: number;
  page_size: number;
  total: number;
};
