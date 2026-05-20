import { useState } from 'react';
import { Link } from 'react-router-dom';
import type { Event } from '../types';
import EventDeleteDialog from './EventDeleteDialog';

interface EventListProps {
  events?: Event[];
  isLoading: boolean;
  isError: boolean;
  isAdmin: boolean;
}

export default function EventList({ events, isLoading, isError, isAdmin }: EventListProps) {
  const [deletingEvent, setDeletingEvent] = useState<Event | null>(null);

  if (isLoading) {
    return <p className="text-text-muted">Loading events...</p>;
  }

  if (isError) {
    return <p className="text-danger-400">Failed to load events. Please try again.</p>;
  }

  if (events && events.length === 0) {
    return <p className="text-text-muted">No events found.</p>;
  }

  return (
    <>
      <table className="w-full border-collapse text-left text-sm">
        <thead>
          <tr className="border-b-2 border-border">
            <th className="px-3 py-2 text-text-muted font-medium">Name</th>
            <th className="px-3 py-2 text-text-muted font-medium">Date</th>
            <th className="px-3 py-2 text-text-muted font-medium">Location</th>
            <th className="px-3 py-2 text-text-muted font-medium">Description</th>
            {isAdmin && <th className="px-3 py-2 text-text-muted font-medium">Actions</th>}
          </tr>
        </thead>
        <tbody>
          {events && events.map((event) => (
            <tr key={event.id} className="border-b border-border hover:bg-surface-muted">
              <td className="px-3 py-2 text-text">{event.name}</td>
              <td className="px-3 py-2 text-text">{event.date}</td>
              <td className="px-3 py-2 text-text">{event.location}</td>
              <td className="px-3 py-2 text-text">{event.description}</td>
              {isAdmin && (
                <td className="px-3 py-2 flex gap-3">
                  <Link to={`/events/${event.id}/edit`} className="text-brand-500 hover:text-brand-600">
                    Edit
                  </Link>
                  <button
                    onClick={() => setDeletingEvent(event)}
                    className="bg-transparent border-none text-danger-400 cursor-pointer p-0 hover:underline text-sm"
                  >
                    Delete
                  </button>
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>

      {deletingEvent && (
        <EventDeleteDialog
          eventId={deletingEvent.id}
          eventName={deletingEvent.name}
          isOpen={true}
          onClose={() => setDeletingEvent(null)}
        />
      )}
    </>
  );
}
