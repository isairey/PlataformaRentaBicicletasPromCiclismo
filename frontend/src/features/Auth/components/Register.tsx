import { Navigate, Link } from 'react-router-dom';
import { useAuth } from '../../../services/useAuth';
import useRegister from '../hooks/useRegister';
import RegisterForm from './RegisterForm';
import type { ApiError } from '../../../types';

export default function Register() {
  const { idToken } = useAuth();
  const mutation = useRegister();

  if (idToken) {
    return <Navigate to="/" replace />;
  }

  return (
    <div className="flex flex-col items-center pt-12 gap-4">
      <RegisterForm
        onSubmit={(payload) => mutation.mutate(payload)}
        isPending={mutation.isPending}
        error={mutation.error as ApiError | null}
      />
      <p className="text-center text-text-muted text-sm">
        Already have an account? <Link to="/login" className="text-brand-500 hover:text-brand-600">Login</Link>
      </p>
    </div>
  );
}
