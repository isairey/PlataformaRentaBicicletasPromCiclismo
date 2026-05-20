import { Navigate } from 'react-router-dom';
import { useAuth } from '../../services/useAuth';
import useLogin from './hooks/useLogin';
import LoginForm from './components/LoginForm';
import type { ApiError } from '../../types';

export default function Auth() {
  const { idToken } = useAuth();
  const mutation = useLogin();

  if (idToken) {
    return <Navigate to="/" replace />;
  }

  return (
    <div className="flex justify-center items-start pt-12">
      <LoginForm
        onSubmit={(payload) => mutation.mutate(payload)}
        isPending={mutation.isPending}
        error={mutation.error as ApiError | null}
      />
    </div>
  );
}
