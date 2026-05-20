import { useState } from "react";
import RentalMap from "./components/RentalMap/RentalMap";
import RentalConfirmDialog from "./components/RentalConfirmDialog";
import ReturnConfirmDialog from "./components/ReturnConfirmDialog";
import RentalPanel from "./components/RentalPanel";
import useCreateRental from "./hooks/useCreateRental";
import useReturnRental from "./hooks/useReturnRental";
import useFetchUserRentals from "./hooks/useFetchUserRentals";
import type { Rental } from "./types";

export default function Rental() {
  const [selectedBikeId, setSelectedBikeId] = useState<string | null>(null);
  const [rentError, setRentError] = useState<string | null>(null);

  const [selectedReturnRental, setSelectedReturnRental] =
    useState<Rental | null>(null);
  const [returnError, setReturnError] = useState<string | null>(null);

  const createRental = useCreateRental();
  const returnRental = useReturnRental();
  const { data: rentals = [], isLoading: isLoadingRentals } =
    useFetchUserRentals();

  function handleBikeClick(bikeId: string) {
    setSelectedBikeId(bikeId);
    setRentError(null);
  }

  function handleRentConfirm() {
    if (!selectedBikeId) return;
    createRental.mutate(
      { bikeId: selectedBikeId },
      {
        onSuccess: () => {
          setSelectedBikeId(null);
          setRentError(null);
        },
        onError: (err) => {
          setRentError(
            err.message ?? "Failed to create rental. Please try again.",
          );
        },
      },
    );
  }

  function handleRentCancel() {
    setSelectedBikeId(null);
    setRentError(null);
  }

  function handleReturnClick(rentalId: string) {
    const rental = rentals.find((r) => r.rentalId === rentalId) ?? null;
    setSelectedReturnRental(rental);
    setReturnError(null);
  }

  function handleReturnConfirm() {
    if (!selectedReturnRental) return;
    returnRental.mutate(selectedReturnRental.rentalId, {
      onSuccess: () => {
        setSelectedReturnRental(null);
        setReturnError(null);
      },
      onError: (err) => {
        setReturnError(
          err.message ?? "Failed to return bike. Please try again.",
        );
      },
    });
  }

  function handleReturnCancel() {
    setSelectedReturnRental(null);
    setReturnError(null);
  }

  return (
    <div className="flex gap-4 h-full">
      <div className="flex-1 min-w-0">
        <RentalMap onBikeClick={handleBikeClick} />
      </div>

      <div className="w-80 shrink-0 overflow-y-auto">
        <h2 className="text-xl font-semibold text-text mb-4">My Rentals</h2>
        <RentalPanel
          rentals={rentals}
          isLoading={isLoadingRentals}
          onReturn={handleReturnClick}
        />
      </div>

      <RentalConfirmDialog
        bikeId={selectedBikeId ?? ""}
        isOpen={selectedBikeId !== null}
        isPending={createRental.isPending}
        errorMessage={rentError ?? undefined}
        onConfirm={handleRentConfirm}
        onCancel={handleRentCancel}
      />

      <ReturnConfirmDialog
        rentalId={selectedReturnRental?.rentalId ?? ""}
        bikeId={selectedReturnRental?.bikeId ?? ""}
        isOpen={selectedReturnRental !== null}
        isPending={returnRental.isPending}
        errorMessage={returnError ?? undefined}
        onConfirm={handleReturnConfirm}
        onCancel={handleReturnCancel}
      />
    </div>
  );
}
