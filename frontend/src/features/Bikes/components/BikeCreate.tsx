import { Link } from 'react-router-dom';
import useCreateBike from '../hooks/useCreateBike';
import BikeForm from './BikeForm';
import type { ApiError } from '../../../types';

export default function BikeCreate() {
  const mutation = useCreateBike();

  return (
    <div>
      <h1 className="text-2xl font-semibold text-text mb-6">Add Bike</h1>
      <BikeForm
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
