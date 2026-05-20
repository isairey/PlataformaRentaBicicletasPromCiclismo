import { useParams, Link } from 'react-router-dom';
import useFetchBike from '../hooks/useFetchBike';
import useUpdateBike from '../hooks/useUpdateBike';
import BikeForm from './BikeForm';
import type { ApiError } from '../../../types';

export default function BikeEdit() {
  const { id } = useParams<{ id: string }>();
  const { data: bike, isLoading, isError } = useFetchBike(id!);
  const mutation = useUpdateBike(id!);

  if (isLoading) {
    return <p className="text-text-muted">Loading bike...</p>;
  }

  if (isError || !bike) {
    return (
      <div>
        <p className="text-text mb-2">Bike not found.</p>
        <Link to="/bikes" className="text-brand-500 hover:text-brand-600 text-sm">&larr; Back to Bikes</Link>
      </div>
    );
  }

  return (
    <div>
      <h1 className="text-2xl font-semibold text-text mb-6">Edit Bike</h1>
      <BikeForm
        key={bike.id}
        defaultValues={bike}
        onSubmit={(payload) => mutation.mutate(payload)}
        isPending={mutation.isPending}
        error={mutation.error as ApiError | null}
      />
      <p className="mt-4">
        <Link to="/bikes" className="text-brand-500 hover:text-brand-600 text-sm">&larr; Cancel</Link>
      </p>
    </div>
  );
}
