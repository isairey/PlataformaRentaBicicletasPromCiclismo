import { useState } from 'react';
import type { FormEvent } from 'react';
import type { EventPayload } from '../types';
import type { ApiError } from '../../../types';

interface EventFormProps {
  defaultValues?: Partial<EventPayload>;
  onSubmit: (payload: EventPayload) => void;
  isPending: boolean;
  error?: ApiError | null;
}

export default function EventForm({ defaultValues, onSubmit, isPending, error }: EventFormProps) {
  const [name, setName] = useState(defaultValues?.name ?? '');
  const [date, setDate] = useState(defaultValues?.date ?? '');
  const [location, setLocation] = useState(defaultValues?.location ?? '');
  const [description, setDescription] = useState(defaultValues?.description ?? '');
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});

  function validate(): boolean {
    const errors: Record<string, string> = {};
    if (!name.trim()) errors.name = 'Name is required';
    if (!date.trim()) errors.date = 'Date is required';
    if (!location.trim()) errors.location = 'Location is required';
    if (!description.trim()) errors.description = 'Description is required';
    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!validate()) return;
    onSubmit({ name: name.trim(), date: date.trim(), location: location.trim(), description: description.trim() });
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
        <div className="text-sm font-medium text-text mb-1">Date *</div>
        <input
          type="date"
          value={date}
          onChange={(e) => setDate(e.target.value)}
          className="w-full px-3 py-2 border border-border rounded focus:outline-none focus:border-brand-300"
        />
        {(fieldErrors.date || getApiFieldError('date')) && (
          <div className="text-danger-400 text-xs mt-1">{fieldErrors.date || getApiFieldError('date')}</div>
        )}
      </label>

      <label>
        <div className="text-sm font-medium text-text mb-1">Location *</div>
        <input
          type="text"
          value={location}
          onChange={(e) => setLocation(e.target.value)}
          className="w-full px-3 py-2 border border-border rounded focus:outline-none focus:border-brand-300"
        />
        {(fieldErrors.location || getApiFieldError('location')) && (
          <div className="text-danger-400 text-xs mt-1">{fieldErrors.location || getApiFieldError('location')}</div>
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
