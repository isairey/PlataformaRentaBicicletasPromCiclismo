import { Link } from 'react-router-dom';
import useFetchRoutes from './hooks/useFetchRoutes';
import RouteList from './components/RouteList';
import { useAuth } from '../../services/useAuth';

export default function EventRoutes() {
  const { data, isLoading, isError } = useFetchRoutes();
  const { isAdmin } = useAuth();

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-semibold text-text">Routes</h1>
        {isAdmin && (
          <Link
            to="/routes/new"
            className="px-5 py-2 bg-brand-500 text-white rounded hover:bg-brand-600 no-underline text-sm"
          >
            Add Route
          </Link>
        )}
      </div>
      <RouteList routes={data} isLoading={isLoading} isError={isError} isAdmin={isAdmin} />
    </div>
  );
}
