import { useFetchAvailableBikes } from './hooks/useFetchAvailableBikes';
import BikeMap from './components/BikeMap';

export default function Map() {
  const { data, isPending, isError } = useFetchAvailableBikes();

  if (isPending) {
    return <p className="text-text-muted p-4">Loading map...</p>;
  }

  if (isError) {
    return <p className="text-danger-400 p-4">Failed to load bike locations. Please try again.</p>;
  }

  if (data.length === 0) {
    return <p className="text-text-muted p-4">No available bikes at the moment.</p>;
  }

  return <BikeMap bikes={data} />;
}
