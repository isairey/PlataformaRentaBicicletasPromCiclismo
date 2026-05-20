export interface BikeLocation {
  bikeId: string;
  latitude: number;
  longitude: number;
}

export interface BikeMarkerProps {
  bike: BikeLocation;
}

export interface BikeMapProps {
  bikes: BikeLocation[];
}
