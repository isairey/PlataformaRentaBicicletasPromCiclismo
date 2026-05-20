import { useState } from 'react';
import type { FormEvent } from 'react';
import type { RegisterPayload } from '../types';
import type { ApiError } from '../../../types';

interface RegisterFormProps {
  onSubmit: (payload: RegisterPayload) => void;
  isPending: boolean;
  error: ApiError | null;
}

export default function RegisterForm({ onSubmit, isPending, error }: RegisterFormProps) {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});

  function validate(): boolean {
    const errors: Record<string, string> = {};
    if (!name.trim()) errors.name = 'Name is required';
    if (!email.includes('@')) errors.email = 'Enter a valid email address';
    if (password.length < 8) errors.password = 'Password must be at least 8 characters';
    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!validate()) return;
    onSubmit({ email, password, Name: name });
  }

  function getApiFieldError(field: string): string | undefined {
    if (error?.error === 'VALIDATION_ERROR' && error.details) {
      return error.details.find((d) => d.toLowerCase().includes(field.toLowerCase()));
    }
    return undefined;
  }

  function getTopLevelError(): string | undefined {
    if (!error) return undefined;
    if (error.error === 'EMAIL_ALREADY_EXISTS') return 'This email is already registered';
    if (error.error === 'WEAK_PASSWORD') return 'The password is too weak';
    if (error.error !== 'VALIDATION_ERROR') return error.message ?? 'An error occurred';
    return undefined;
  }

  const topError = getTopLevelError();

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4 w-full max-w-sm text-left">
      <h1 className="text-2xl font-semibold text-text text-center">Register</h1>

      {topError && (
        <div className="text-danger-400 text-sm p-2 border border-danger-400 rounded">
          {topError}
        </div>
      )}

      <label>
        <div className="text-sm font-medium text-text mb-1">Name</div>
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="w-full px-3 py-2 border border-border rounded focus:outline-none focus:border-brand-300"
        />
        {(fieldErrors.name || getApiFieldError('name')) && (
          <div className="text-danger-400 text-xs mt-1">{fieldErrors.name || getApiFieldError('name')}</div>
        )}
      </label>

      <label>
        <div className="text-sm font-medium text-text mb-1">Email</div>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full px-3 py-2 border border-border rounded focus:outline-none focus:border-brand-300"
        />
        {(fieldErrors.email || getApiFieldError('email')) && (
          <div className="text-danger-400 text-xs mt-1">{fieldErrors.email || getApiFieldError('email')}</div>
        )}
      </label>

      <label>
        <div className="text-sm font-medium text-text mb-1">Password</div>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full px-3 py-2 border border-border rounded focus:outline-none focus:border-brand-300"
        />
        {(fieldErrors.password || getApiFieldError('password')) && (
          <div className="text-danger-400 text-xs mt-1">{fieldErrors.password || getApiFieldError('password')}</div>
        )}
      </label>

      <button
        type="submit"
        disabled={isPending}
        className={`w-full py-2.5 bg-brand-500 text-white rounded hover:bg-brand-600 ${isPending ? 'opacity-70 cursor-not-allowed' : 'cursor-pointer'}`}
      >
        {isPending ? 'Registering...' : 'Register'}
      </button>
    </form>
  );
}
