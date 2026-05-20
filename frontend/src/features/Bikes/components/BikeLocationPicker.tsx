import L from "leaflet";
import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";
import {
  MapContainer,
  Marker,
  TileLayer,
  ZoomControl,
  useMapEvents,
} from "react-leaflet";

const DefaultIcon = L.icon({
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

L.Marker.prototype.options.icon = DefaultIcon;

const DEFAULT_LAT = 6.244;
const DEFAULT_LNG = -75.5812;

function MapClickHandler({
  onPosition,
}: {
  onPosition: (lat: number, lng: number) => void;
}) {
  useMapEvents({
    click(e) {
      onPosition(e.latlng.lat, e.latlng.lng);
    },
  });
  return null;
}

interface BikeLocationPickerProps {
  latitude: string;
  longitude: string;
  onChange: (lat: number, lng: number) => void;
}

function parsePosition(latitude: string, longitude: string): [number, number] {
  const lat = Number(latitude);
  const lng = Number(longitude);
  const okLat = Number.isFinite(lat) && lat >= -90 && lat <= 90;
  const okLng = Number.isFinite(lng) && lng >= -180 && lng <= 180;
  return [
    okLat ? lat : DEFAULT_LAT,
    okLng ? lng : DEFAULT_LNG,
  ];
}

export default function BikeLocationPicker({
  latitude,
  longitude,
  onChange,
}: BikeLocationPickerProps) {
  const position = parsePosition(latitude, longitude);

  return (
    <div className="flex flex-col gap-2">
      <div className="text-sm font-medium text-text">Location *</div>
      <p className="text-xs text-text-muted">
        Click on the map or drag the pin to set latitude and longitude.
      </p>
      <div
        className="rounded border border-border overflow-hidden w-full"
        style={{ height: 280 }}
      >
        <MapContainer
          center={position}
          zoom={13}
          style={{ height: "100%", width: "100%" }}
          zoomControl={false}
          scrollWheelZoom
        >
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          />
          <ZoomControl position="topright" />
          <MapClickHandler onPosition={onChange} />
          <Marker
            position={position}
            draggable
            eventHandlers={{
              dragend(e) {
                const p = e.target.getLatLng();
                onChange(p.lat, p.lng);
              },
            }}
          />
        </MapContainer>
      </div>
      <p className="text-xs text-text-muted font-mono">
        {Number.isFinite(Number(latitude)) && Number.isFinite(Number(longitude))
          ? `${Number(latitude).toFixed(6)}, ${Number(longitude).toFixed(6)}`
          : "—"}
      </p>
    </div>
  );
}
