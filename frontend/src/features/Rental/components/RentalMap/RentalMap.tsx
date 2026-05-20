import L from 'leaflet';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';
import { MapContainer, Marker, Popup, TileLayer, ZoomControl } from 'react-leaflet';
import useFetchAvailableBikes from './hooks/useFetchAvailableBikes';

const DefaultIcon = L.icon({
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

L.Marker.prototype.options.icon = DefaultIcon;

interface RentalMapProps {
  onBikeClick: (bikeId: string) => void;
}

export default function RentalMap({ onBikeClick }: RentalMapProps) {
  const { data: bikes = [], isLoading, isError } = useFetchAvailableBikes();

  return (
    <div className="flex flex-col gap-2 h-full">
      <h1 className="text-2xl font-semibold text-text">Rent a Bike</h1>
      {isLoading && (
        <p className="text-sm text-text-muted">Loading available bikes…</p>
      )}
      {isError && (
        <p className="text-sm text-danger-400">Failed to load bike locations.</p>
      )}
      <MapContainer
        center={[6.244, -75.5812]}
        zoom={13}
        style={{ height: '560px', width: '100%' }}
        zoomControl={false}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />
        <ZoomControl position="topright" />
        {bikes.map((bike) => (
          <Marker key={bike.bikeId} position={[bike.latitude, bike.longitude]}>
            <Popup>
              <div className="flex flex-col gap-1">
                <p className="font-semibold text-sm">Bike</p>
                <p className="text-xs text-text-muted">ID: {bike.bikeId.slice(0, 8)}…</p>
                <div className="flex gap-2 justify-between items-center mt-1">
                  <p className="text-xs text-green-600">Available</p>
                  <button
                    className="px-3 py-1 bg-brand-500 text-white text-xs rounded hover:bg-brand-600"
                    onClick={() => onBikeClick(bike.bikeId)}
                  >
                    Rent
                  </button>
                </div>
              </div>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </div>
  );
}
