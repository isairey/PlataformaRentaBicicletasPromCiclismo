import type { Rental } from '../types';

interface ActiveRentalCardProps {
  rental: Rental;
  onReturn: (rentalId: string) => void;
}

export default function ActiveRentalCard({ rental, onReturn }: ActiveRentalCardProps) {
  const start = new Date(rental.startTime).toLocaleString();

  return (
    <div className="border border-border rounded-lg p-4 flex flex-col gap-2 bg-surface">
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-green-100 text-green-700">
          Active
        </span>
        <span className="text-xs text-text-muted font-mono">
          {rental.bikeId.slice(0, 8)}…
        </span>
      </div>
      <p className="text-sm text-text-muted">Started: {start}</p>
      <button
        className="mt-1 w-full px-3 py-2 text-sm rounded border border-danger-400 text-danger-400 hover:bg-danger-400 hover:text-white transition-colors"
        onClick={() => onReturn(rental.rentalId)}
      >
        Return Bike
      </button>
    </div>
  );
}
