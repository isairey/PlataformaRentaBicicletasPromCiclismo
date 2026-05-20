import { Link } from 'react-router-dom';
import useCreateRoute from '../hooks/useCreateRoute';
import RouteForm from './RouteForm';
import type { ApiError } from '../../../types';

export default function RouteCreate() {
  const mutation = useCreateRoute();

  return (
    <div>
      <h1 className="text-2xl font-semibold text-text mb-6">Add Route</h1>
      <RouteForm
        onSubmit={(payload) => mutation.mutate(payload)}
        isPending={mutation.isPending}
        error={mutation.error as ApiError | null}
      />
      <p className="mt-4">
        <Link to="/routes" className="text-brand-500 hover:text-brand-600 text-sm">&larr; Cancel</Link>
      </p>
    </div>
  );
}
