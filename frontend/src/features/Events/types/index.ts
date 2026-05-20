export interface Event {
  id: number;
  name: string;
  date: string;
  location: string;
  description: string;
  createdAt: string;
  updatedAt: string;
}

export interface Competition {
  id: number;
  name: string;
  startDate: string;
  endDate: string;
  description: string;
  type: string;
  createdAt: string;
  updatedAt: string;
}

export interface Route {
  id: number;
  name: string;
  distance: number;
  difficulty: string;
  description: string;
  coordinates: unknown;
  createdAt: string;
  updatedAt: string;
}

export interface EventPayload {
  name: string;
  date: string;
  location: string;
  description: string;
}

export interface CompetitionPayload {
  name: string;
  startDate: string;
  endDate: string;
  description: string;
  type: string;
}

export interface RoutePayload {
  name: string;
  distance: number;
  difficulty: string;
  description: string;
  coordinates?: unknown;
}
