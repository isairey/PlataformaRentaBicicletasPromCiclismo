export type RentalStatus = 'ACTIVE' | 'COMPLETED';

export interface Rental {
  rentalId: string;
  bikeId: string;
  userId: string;
  startTime: string;
  endTime: string | null;
  status: RentalStatus;
}

export interface CreateRentalPayload {
  bikeId: string;
}
