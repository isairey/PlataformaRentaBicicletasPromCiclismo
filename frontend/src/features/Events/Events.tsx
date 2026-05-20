import { Link } from 'react-router-dom';
import useFetchEvents from './hooks/useFetchEvents';
import EventList from './components/EventList';
import { useAuth } from '../../services/useAuth';

export default function Events() {
  const { data, isLoading, isError } = useFetchEvents();
  const { isAdmin } = useAuth();

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-semibold text-text">Events</h1>
        {isAdmin && (
          <Link
            to="/events/new"
            className="px-5 py-2 bg-brand-500 text-white rounded hover:bg-brand-600 no-underline text-sm"
          >
            Add Event
          </Link>
        )}
      </div>
      <EventList events={data} isLoading={isLoading} isError={isError} isAdmin={isAdmin} />
    </div>
  );
}
