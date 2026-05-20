import type { AxiosInstance } from 'axios';
import { AxiosError } from 'axios';
import type { Event, Competition, Route, EventPayload, CompetitionPayload, RoutePayload } from '../types';
import type { ApiError } from '../../../types';

// ── Events ───────────────────────────────────────────────────────────────────

export async function fetchEvents(api: AxiosInstance): Promise<Event[]> {
  const { data } = await api.get<Event[]>('events/events');
  return data;
}

export async function createEvent(
  api: AxiosInstance,
  payload: EventPayload,
): Promise<Event> {
  try {
    const { data } = await api.post<Event>('events/events', payload);
    return data;
  } catch (err) {
    if (err instanceof AxiosError && err.response?.data) {
      throw err.response.data as ApiError;
    }
    throw err;
  }
}

export async function updateEvent(
  api: AxiosInstance,
  id: number,
  payload: EventPayload,
): Promise<Event> {
  try {
    const { data } = await api.put<Event>(`events/events/${id}`, payload);
    return data;
  } catch (err) {
    if (err instanceof AxiosError && err.response?.data) {
      throw err.response.data as ApiError;
    }
    throw err;
  }
}

export async function deleteEvent(api: AxiosInstance, id: number): Promise<void> {
  await api.delete(`events/events/${id}`);
}

// ── Competitions ─────────────────────────────────────────────────────────────

export async function fetchCompetitions(api: AxiosInstance): Promise<Competition[]> {
  const { data } = await api.get<Competition[]>('events/competitions');
  return data;
}

export async function createCompetition(
  api: AxiosInstance,
  payload: CompetitionPayload,
): Promise<Competition> {
  try {
    const { data } = await api.post<Competition>('events/competitions', payload);
    return data;
  } catch (err) {
    if (err instanceof AxiosError && err.response?.data) {
      throw err.response.data as ApiError;
    }
    throw err;
  }
}

export async function updateCompetition(
  api: AxiosInstance,
  id: number,
  payload: CompetitionPayload,
): Promise<Competition> {
  try {
    const { data } = await api.put<Competition>(`events/competitions/${id}`, payload);
    return data;
  } catch (err) {
    if (err instanceof AxiosError && err.response?.data) {
      throw err.response.data as ApiError;
    }
    throw err;
  }
}

export async function deleteCompetition(api: AxiosInstance, id: number): Promise<void> {
  await api.delete(`events/competitions/${id}`);
}

// ── Routes ────────────────────────────────────────────────────────────────────

export async function fetchRoutes(api: AxiosInstance): Promise<Route[]> {
  const { data } = await api.get<Route[]>('events/routes');
  return data;
}

export async function createRoute(
  api: AxiosInstance,
  payload: RoutePayload,
): Promise<Route> {
  try {
    const { data } = await api.post<Route>('events/routes', payload);
    return data;
  } catch (err) {
    if (err instanceof AxiosError && err.response?.data) {
      throw err.response.data as ApiError;
    }
    throw err;
  }
}

export async function updateRoute(
  api: AxiosInstance,
  id: number,
  payload: RoutePayload,
): Promise<Route> {
  try {
    const { data } = await api.put<Route>(`events/routes/${id}`, payload);
    return data;
  } catch (err) {
    if (err instanceof AxiosError && err.response?.data) {
      throw err.response.data as ApiError;
    }
    throw err;
  }
}

export async function deleteRoute(api: AxiosInstance, id: number): Promise<void> {
  await api.delete(`events/routes/${id}`);
}
