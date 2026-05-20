import { useState } from 'react';
import type { FormEvent } from 'react';
import type { CompetitionPayload } from '../types';
import type { ApiError } from '../../../types';

interface CompetitionFormProps {
  defaultValues?: Partial<CompetitionPayload>;
  onSubmit: (payload: CompetitionPayload) => void;
  isPending: boolean;
  error?: ApiError | null;
}

export default function CompetitionForm({ defaultValues, onSubmit, isPending, error }: CompetitionFormProps) {
  const [name, setName] = useState(defaultValues?.name ?? '');
  const [type, setType] = useState(defaultValues?.type ?? '');
  const [startDate, setStartDate] = useState(defaultValues?.startDate ?? '');
  const [endDate, setEndDate] = useState(defaultValues?.endDate ?? '');
  const [description, setDescription] = useState(defaultValues?.description ?? '');
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});

  function validate(): boolean {
    const errors: Record<string, string> = {};
    if (!name.trim()) errors.name = 'Name is required';
    if (!type.trim()) errors.type = 'Type is required';
    if (!startDate.trim()) errors.startDate = 'Start date is required';
    if (!endDate.trim()) {
      errors.endDate = 'End date is required';
    } else if (startDate && endDate <= startDate) {
      errors.endDate = 'End date must be after start date';
    }
    if (!description.trim()) errors.description = 'Description is required';
    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!validate()) return;
    onSubmit({
      name: name.trim(),
      type: type.trim(),
      startDate: startDate.trim(),
      endDate: endDate.trim(),
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
        <div className="text-sm font-medium text-text mb-1">Type *</div>
        <input
          type="text"
          value={type}
          onChange={(e) => setType(e.target.value)}
          className="w-full px-3 py-2 border border-border rounded focus:outline-none focus:border-brand-300"
        />
        {(fieldErrors.type || getApiFieldError('type')) && (
          <div className="text-danger-400 text-xs mt-1">{fieldErrors.type || getApiFieldError('type')}</div>
        )}
      </label>

      <label>
        <div className="text-sm font-medium text-text mb-1">Start Date *</div>
        <input
          type="date"
          value={startDate}
          onChange={(e) => setStartDate(e.target.value)}
          className="w-full px-3 py-2 border border-border rounded focus:outline-none focus:border-brand-300"
        />
        {(fieldErrors.startDate || getApiFieldError('startDate')) && (
          <div className="text-danger-400 text-xs mt-1">{fieldErrors.startDate || getApiFieldError('startDate')}</div>
        )}
      </label>

      <label>
        <div className="text-sm font-medium text-text mb-1">End Date *</div>
        <input
          type="date"
          value={endDate}
          onChange={(e) => setEndDate(e.target.value)}
          className="w-full px-3 py-2 border border-border rounded focus:outline-none focus:border-brand-300"
        />
        {(fieldErrors.endDate || getApiFieldError('endDate')) && (
          <div className="text-danger-400 text-xs mt-1">{fieldErrors.endDate || getApiFieldError('endDate')}</div>
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
