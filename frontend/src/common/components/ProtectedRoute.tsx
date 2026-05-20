import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../../services/useAuth';

export default function ProtectedRoute() {
  const { idToken } = useAuth();

  if (idToken === null) {
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
}
