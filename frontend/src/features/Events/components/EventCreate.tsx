import { Link } from 'react-router-dom';
import useCreateEvent from '../hooks/useCreateEvent';
import EventForm from './EventForm';
import type { ApiError } from '../../../types';

export default function EventCreate() {
  const mutation = useCreateEvent();

  return (
    <div>
      <h1 className="text-2xl font-semibold text-text mb-6">Add Event</h1>
      <EventForm
        onSubmit={(payload) => mutation.mutate(payload)}
        isPending={mutation.isPending}
        error={mutation.error as ApiError | null}
      />
      <p className="mt-4">
        <Link to="/events" className="text-brand-500 hover:text-brand-600 text-sm">&larr; Cancel</Link>
      </p>
    </div>
  );
}
