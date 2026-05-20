import { useState } from 'react';
import type { FormEvent } from 'react';
import type { RoutePayload } from '../types';
import type { ApiError } from '../../../types';

interface RouteFormProps {
  defaultValues?: Partial<RoutePayload>;
  onSubmit: (payload: RoutePayload) => void;
  isPending: boolean;
  error?: ApiError | null;
}

export default function RouteForm({ defaultValues, onSubmit, isPending, error }: RouteFormProps) {
  const [name, setName] = useState(defaultValues?.name ?? '');
  const [distance, setDistance] = useState(defaultValues?.distance?.toString() ?? '');
  const [difficulty, setDifficulty] = useState(defaultValues?.difficulty ?? '');
  const [description, setDescription] = useState(defaultValues?.description ?? '');
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});

  function validate(): boolean {
    const errors: Record<string, string> = {};
    if (!name.trim()) errors.name = 'Name is required';
    if (!distance.trim()) {
      errors.distance = 'Distance is required';
    } else if (isNaN(Number(distance)) || Number(distance) <= 0) {
      errors.distance = 'Distance must be a number greater than 0';
    }
    if (!difficulty.trim()) errors.difficulty = 'Difficulty is required';
    if (!description.trim()) errors.description = 'Description is required';
    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!validate()) return;
    onSubmit({
      name: name.trim(),
      distance: Number(distance),
      difficulty: difficulty.trim(),
      description: description.trim(),
    });
  }

  function getApiFieldError(field: string): string | undefined {
    if (error?.error === 'VALIDATION_ERROR' && error.details) {
      return error.details.find((d) => d.toLowerCase().includes(field.toLowerCase()));
    }
    return undefined;
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4 w-full max-w-lg text-left">
      {error && error.error !== 'VALIDATION_ERROR' && (
        <div className="text-danger-400 text-sm p-2 border border-danger-400 rounded">
          {error.message ?? 'An error occurred'}
        </div>
      )}

      <label>
        <div className="text-sm font-medium text-text mb-1">Name *</div>
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
        <div className="text-sm font-medium text-text mb-1">Distance *</div>
        <input
          type="number"
          step="any"
          value={distance}
          onChange={(e) => setDistance(e.target.value)}
          className="w-full px-3 py-2 border border-border rounded focus:outline-none focus:border-brand-300"
        />
        {(fieldErrors.distance || getApiFieldError('distance')) && (
          <div className="text-danger-400 text-xs mt-1">{fieldErrors.distance || getApiFieldError('distance')}</div>
        )}
      </label>

      <label>
        <div className="text-sm font-medium text-text mb-1">Difficulty *</div>
        <input
          type="text"
          value={difficulty}
          onChange={(e) => setDifficulty(e.target.value)}
          placeholder="e.g. Easy, Moderate, Hard"
          className="w-full px-3 py-2 border border-border rounded focus:outline-none focus:border-brand-300"
        />
        {(fieldErrors.difficulty || getApiFieldError('difficulty')) && (
          <div className="text-danger-400 text-xs mt-1">{fieldErrors.difficulty || getApiFieldError('difficulty')}</div>
        )}
      </label>

      <label>
        <div className="text-sm font-medium text-text mb-1">Description *</div>
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          rows={4}
          className="w-full px-3 py-2 border border-border rounded focus:outline-none focus:border-brand-300 resize-none"
        />
        {(fieldErrors.description || getApiFieldError('description')) && (
          <div className="text-danger-400 text-xs mt-1">{fieldErrors.description || getApiFieldError('description')}</div>
        )}
      </label>

      <button
        type="submit"
        disabled={isPending}
        className={`px-5 py-2 bg-brand-500 text-white rounded hover:bg-brand-600 self-start ${isPending ? 'opacity-70 cursor-not-allowed' : 'cursor-pointer'}`}
      >
        {isPending ? 'Saving...' : 'Save'}
      </button>
    </form>
  );
}
