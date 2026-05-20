import type { Rental } from '../types';
import ActiveRentalCard from './ActiveRentalCard';
import CompletedRentalCard from './CompletedRentalCard';

interface RentalPanelProps {
  rentals: Rental[];
  isLoading: boolean;
  onReturn: (rentalId: string) => void;
}

export default function RentalPanel({ rentals, isLoading, onReturn }: RentalPanelProps) {
  const active = rentals.filter((r) => r.status === 'ACTIVE');
  const completed = rentals.filter((r) => r.status === 'COMPLETED');

  if (isLoading) {
    return <p className="text-sm text-text-muted">Loading rentals…</p>;
  }

  if (rentals.length === 0) {
    return (
      <p className="text-sm text-text-muted italic">
        No rentals yet. Rent a bike from the map!
      </p>
    );
  }

  return (
    <div className="flex flex-col gap-6">
      {active.length > 0 && (
        <section>
          <h3 className="text-sm font-semibold text-text uppercase tracking-wide mb-3">
            Active Rentals
          </h3>
          <div className="flex flex-col gap-3">
            {active.map((rental) => (
              <ActiveRentalCard key={rental.rentalId} rental={rental} onReturn={onReturn} />
            ))}
          </div>
        </section>
      )}

      {completed.length > 0 && (
        <section>
          <h3 className="text-sm font-semibold text-text-muted uppercase tracking-wide mb-3">
            History
          </h3>
          <div className="flex flex-col gap-3">
            {completed.map((rental) => (
              <CompletedRentalCard key={rental.rentalId} rental={rental} />
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
