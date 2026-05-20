import { useParams, Link } from 'react-router-dom';
import useFetchEvents from '../hooks/useFetchEvents';
import useUpdateEvent from '../hooks/useUpdateEvent';
import EventForm from './EventForm';
import type { ApiError } from '../../../types';

export default function EventEdit() {
  const { id } = useParams<{ id: string }>();
  const eventId = Number(id);
  const { data: events, isLoading, isError } = useFetchEvents();
  const event = events?.find((e) => e.id === eventId);
  const mutation = useUpdateEvent(eventId);

  if (isLoading) {
    return <p className="text-text-muted">Loading event...</p>;
  }

  if (isError || !event) {
    return (
      <div>
        <p className="text-text mb-2">Event not found.</p>
        <Link to="/events" className="text-brand-500 hover:text-brand-600 text-sm">&larr; Back to Events</Link>
      </div>
    );
  }

  return (
    <div>
      <h1 className="text-2xl font-semibold text-text mb-6">Edit Event</h1>
      <EventForm
        key={event.id}
        defaultValues={event}
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
