import type { Rental } from '../types';

interface CompletedRentalCardProps {
  rental: Rental;
}

export default function CompletedRentalCard({ rental }: CompletedRentalCardProps) {
  const start = new Date(rental.startTime).toLocaleString();
  const end = rental.endTime ? new Date(rental.endTime).toLocaleString() : '—';

  return (
    <div className="border border-border rounded-lg p-4 flex flex-col gap-1 bg-surface opacity-70">
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium px-2 py-0.5 rounded-full bg-surface-alt text-text-muted">
          Completed
        </span>
        <span className="text-xs text-text-muted font-mono">
          {rental.bikeId.slice(0, 8)}…
        </span>
      </div>
      <p className="text-xs text-text-muted">Start: {start}</p>
      <p className="text-xs text-text-muted">End: {end}</p>
    </div>
  );
}
