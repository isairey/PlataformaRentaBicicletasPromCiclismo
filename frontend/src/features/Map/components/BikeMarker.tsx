import { Marker, Popup } from "react-leaflet";
import type { BikeMarkerProps } from "../types";

export default function BikeMarker({ bike }: BikeMarkerProps) {
  return (
    <Marker position={[bike.latitude, bike.longitude]}>
      <Popup>
        <div>
          <p className="font-semibold">Bike</p>
          <p className="font-semibold text-small">ID: {bike.bikeId}</p>
          <p className="text-sm text-green-600 mt-1">Available</p>
        </div>
      </Popup>
    </Marker>
  );
}
