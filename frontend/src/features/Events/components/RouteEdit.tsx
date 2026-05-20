import { useParams, Link } from 'react-router-dom';
import useFetchRoutes from '../hooks/useFetchRoutes';
import useUpdateRoute from '../hooks/useUpdateRoute';
import RouteForm from './RouteForm';
import type { ApiError } from '../../../types';

export default function RouteEdit() {
  const { id } = useParams<{ id: string }>();
  const routeId = Number(id);
  const { data: routes, isLoading, isError } = useFetchRoutes();
  const route = routes?.find((r) => r.id === routeId);
  const mutation = useUpdateRoute(routeId);

  if (isLoading) {
    return <p className="text-text-muted">Loading route...</p>;
  }

  if (isError || !route) {
    return (
      <div>
        <p className="text-text mb-2">Route not found.</p>
        <Link to="/routes" className="text-brand-500 hover:text-brand-600 text-sm">&larr; Back to Routes</Link>
      </div>
    );
  }

  return (
    <div>
      <h1 className="text-2xl font-semibold text-text mb-6">Edit Route</h1>
      <RouteForm
        key={route.id}
        defaultValues={route}
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
