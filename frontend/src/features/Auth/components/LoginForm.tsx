import { useState } from 'react';
import type { FormEvent } from 'react';
import { Link } from 'react-router-dom';
import type { LoginPayload } from '../types';
import type { ApiError } from '../../../types';

interface LoginFormProps {
  onSubmit: (payload: LoginPayload) => void;
  isPending: boolean;
  error: ApiError | null;
}

export default function LoginForm({ onSubmit, isPending, error }: LoginFormProps) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  function getErrorMessage(): string | undefined {
    if (!error) return undefined;
    if (error.error === 'INVALID_CREDENTIALS' || error.error === 'USER_NOT_FOUND') {
      return 'Invalid email or password';
    }
    if (error.error === 'USER_DISABLED') return 'This account has been disabled';
    return error.message ?? 'An error occurred';
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    onSubmit({ email, password });
  }

  const errorMessage = getErrorMessage();

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4 w-full max-w-sm text-left">
      <h1 className="text-2xl font-semibold text-text text-center">Login</h1>

      {errorMessage && (
        <div className="text-danger-400 text-sm p-2 border border-danger-400 rounded">
          {errorMessage}
        </div>
      )}

      <label>
        <div className="text-sm font-medium text-text mb-1">Email</div>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full px-3 py-2 border border-border rounded focus:outline-none focus:border-brand-300"
        />
      </label>

      <label>
        <div className="text-sm font-medium text-text mb-1">Password</div>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full px-3 py-2 border border-border rounded focus:outline-none focus:border-brand-300"
        />
      </label>

      <button
        type="submit"
        disabled={isPending}
        className={`w-full py-2.5 bg-brand-500 text-white rounded hover:bg-brand-600 ${isPending ? 'opacity-70 cursor-not-allowed' : 'cursor-pointer'}`}
      >
        {isPending ? 'Logging in...' : 'Login'}
      </button>

      <p className="text-center text-sm text-text-muted">
        Don&apos;t have an account?{' '}
        <Link to="/register" className="text-brand-500 hover:text-brand-600">Register</Link>
      </p>
    </form>
  );
}
