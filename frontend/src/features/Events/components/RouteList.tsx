import { useState } from 'react';
import { Link } from 'react-router-dom';
import type { Route } from '../types';
import RouteDeleteDialog from './RouteDeleteDialog';

interface RouteListProps {
  routes?: Route[];
  isLoading: boolean;
  isError: boolean;
  isAdmin: boolean;
}

export default function RouteList({ routes, isLoading, isError, isAdmin }: RouteListProps) {
  const [deletingRoute, setDeletingRoute] = useState<Route | null>(null);

  if (isLoading) {
    return <p className="text-text-muted">Loading routes...</p>;
  }

  if (isError) {
    return <p className="text-danger-400">Failed to load routes. Please try again.</p>;
  }

  if (routes && routes.length === 0) {
    return <p className="text-text-muted">No routes found.</p>;
  }

  return (
    <>
      <table className="w-full border-collapse text-left text-sm">
        <thead>
          <tr className="border-b-2 border-border">
            <th className="px-3 py-2 text-text-muted font-medium">Name</th>
            <th className="px-3 py-2 text-text-muted font-medium">Distance</th>
            <th className="px-3 py-2 text-text-muted font-medium">Difficulty</th>
            <th className="px-3 py-2 text-text-muted font-medium">Description</th>
            {isAdmin && <th className="px-3 py-2 text-text-muted font-medium">Actions</th>}
          </tr>
        </thead>
        <tbody>
          {routes && routes.map((route) => (
            <tr key={route.id} className="border-b border-border hover:bg-surface-muted">
              <td className="px-3 py-2 text-text">{route.name}</td>
              <td className="px-3 py-2 text-text">{route.distance}</td>
              <td className="px-3 py-2 text-text">{route.difficulty}</td>
              <td className="px-3 py-2 text-text">{route.description}</td>
              {isAdmin && (
                <td className="px-3 py-2 flex gap-3">
                  <Link to={`/routes/${route.id}/edit`} className="text-brand-500 hover:text-brand-600">
                    Edit
                  </Link>
                  <button
                    onClick={() => setDeletingRoute(route)}
                    className="bg-transparent border-none text-danger-400 cursor-pointer p-0 hover:underline text-sm"
                  >
                    Delete
                  </button>
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>

      {deletingRoute && (
        <RouteDeleteDialog
          routeId={deletingRoute.id}
          routeName={deletingRoute.name}
          isOpen={true}
          onClose={() => setDeletingRoute(null)}
        />
      )}
    </>
  );
}
