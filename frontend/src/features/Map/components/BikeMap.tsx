import L from "leaflet";
import markerIcon from "leaflet/dist/images/marker-icon.png";
import markerShadow from "leaflet/dist/images/marker-shadow.png";
import { MapContainer, TileLayer, ZoomControl } from "react-leaflet";
import BikeMarker from "./BikeMarker";
import type { BikeMapProps } from "../types";

const DefaultIcon = L.icon({
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

L.Marker.prototype.options.icon = DefaultIcon;

export default function BikeMap({ bikes }: BikeMapProps) {
  return (
    <div className="h-(100vh - 14rem) w-full gap-4 flex flex-col">
      <h1 className="text-2xl font-semibold text-text">Bike Map</h1>
      <MapContainer
        center={[6.244, -75.5812]}
        zoom={13}
        style={{ height: "600px", width: "100%" }}
        zoomControl={false}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />
        <ZoomControl position="topright" />
        {bikes.map((bike) => (
          <BikeMarker key={bike.bikeId} bike={bike} />
        ))}
      </MapContainer>
    </div>
  );
}
