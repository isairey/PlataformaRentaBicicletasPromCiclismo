import { useState } from "react";
import { Link } from "react-router-dom";
import type { Bike } from "../types";
import BikeDeleteDialog from "./BikeDeleteDialog";
import type { BikeData } from "../types";

interface BikeListProps {
  bikeData?: BikeData;
  isLoading: boolean;
  isError: boolean;
}

export default function BikeList({
  bikeData,
  isLoading,
  isError,
}: BikeListProps) {
  const [deletingBike, setDeletingBike] = useState<Bike | null>(null);

  if (isLoading) {
    return <p className="text-text-muted">Loading bikes...</p>;
  }

  if (isError) {
    return (
      <p className="text-danger-400">Failed to load bikes. Please try again.</p>
    );
  }

  if (bikeData && bikeData.bikes.length === 0) {
    return (
      <p className="text-text-muted">
        No bikes yet.{" "}
        <Link to="/bikes/new" className="text-brand-500 hover:text-brand-600">
          Add your first bike &rarr;
        </Link>
      </p>
    );
  }

  return (
    <>
      <table className="w-full border-collapse text-left text-sm">
        <thead>
          <tr className="border-b-2 border-border">
            <th className="px-3 py-2 text-text-muted font-medium">Brand</th>
            <th className="px-3 py-2 text-text-muted font-medium">Type</th>
            <th className="px-3 py-2 text-text-muted font-medium">Colour</th>
            <th className="px-3 py-2 text-text-muted font-medium">State</th>
            <th className="px-3 py-2 text-text-muted font-medium">Actions</th>
          </tr>
        </thead>
        <tbody>
          { bikeData && bikeData.bikes.map((bike) => (
            <tr
              key={bike.id}
              className="border-b border-border hover:bg-surface-muted"
            >
              <td className="px-3 py-2 text-text">{bike.brand}</td>
              <td className="px-3 py-2 text-text">{bike.type}</td>
              <td className="px-3 py-2 text-text">{bike.colour}</td>
              <td className="px-3 py-2 text-text">{bike.state ?? "—"}</td>
              <td className="px-3 py-2 flex gap-3">
                <Link
                  to={`/bikes/${bike.id}/edit`}
                  className="text-brand-500 hover:text-brand-600"
                >
                  Edit
                </Link>
                <button
                  onClick={() => setDeletingBike(bike)}
                  className="bg-transparent border-none text-danger-400 cursor-pointer p-0 hover:underline text-sm"
                >
                  Delete
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {deletingBike && (
        <BikeDeleteDialog
          bikeId={deletingBike.id}
          bikeName={`${deletingBike.brand} (${deletingBike.type})`}
          isOpen={true}
          onClose={() => setDeletingBike(null)}
        />
      )}
    </>
  );
}
