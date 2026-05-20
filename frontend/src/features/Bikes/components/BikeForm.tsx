import { useState } from "react";
import type { FormEvent } from "react";
import type { BikePayload } from "../types";
import { BIKE_STATE_OPTIONS, BIKE_TYPE_OPTIONS } from "../types";
import type { ApiError } from "../../../types";
import BikeLocationPicker from "./BikeLocationPicker";

const DEFAULT_LAT = 6.244;
const DEFAULT_LNG = -75.5812;

interface BikeFormProps {
  defaultValues?: Partial<BikePayload>;
  onSubmit: (payload: BikePayload) => void;
  isPending: boolean;
  error?: ApiError | null;
}

export default function BikeForm({
  defaultValues,
  onSubmit,
  isPending,
  error,
}: BikeFormProps) {
  const [brand, setBrand] = useState(defaultValues?.brand ?? "");
  const initialType =
    defaultValues?.type &&
    BIKE_TYPE_OPTIONS.includes(defaultValues.type as (typeof BIKE_TYPE_OPTIONS)[number])
      ? defaultValues.type
      : "";
  const [type, setType] = useState(initialType);
  const [colour, setColour] = useState(defaultValues?.colour ?? "");
  const [latitude, setLatitude] = useState(
    () =>
      defaultValues?.latitude != null
        ? String(defaultValues.latitude)
        : String(DEFAULT_LAT),
  );
  const [longitude, setLongitude] = useState(
    () =>
      defaultValues?.longitude != null
        ? String(defaultValues.longitude)
        : String(DEFAULT_LNG),
  );

  function setPositionFromMap(lat: number, lng: number) {
    setLatitude(lat.toFixed(6));
    setLongitude(lng.toFixed(6));
  }
  const initialStateRaw = defaultValues?.state ?? "Free";
  const initialState = BIKE_STATE_OPTIONS.includes(
    initialStateRaw as (typeof BIKE_STATE_OPTIONS)[number],
  )
    ? initialStateRaw
    : "Free";
  const [state, setStatus] = useState(initialState);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});

  function validate(): boolean {
    const errors: Record<string, string> = {};
    if (!brand.trim()) errors.brand = "Brand is required";
    if (!type.trim()) errors.type = "Select a bike type";
    if (!colour.trim()) errors.colour = "Colour is required";
    if (!latitude.trim()) {
      errors.latitude = "Latitude is required";
    } else if (
      isNaN(Number(latitude)) ||
      Number(latitude) < -90 ||
      Number(latitude) > 90
    ) {
      errors.latitude = "Latitude must be a number between -90 and 90";
    }
    if (!longitude.trim()) {
      errors.longitude = "Longitude is required";
    } else if (
      isNaN(Number(longitude)) ||
      Number(longitude) < -180 ||
      Number(longitude) > 180
    ) {
      errors.longitude = "Longitude must be a number between -180 and 180";
    }
    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!validate()) return;
    const payload: BikePayload = {
      brand: brand.trim(),
      type: type.trim(),
      colour: colour.trim(),
      latitude: Number(latitude),
      longitude: Number(longitude),
    };
    payload.state = state;
    onSubmit(payload);
  }

  function getApiFieldError(field: string): string | undefined {
    if (error?.error === "VALIDATION_ERROR" && error.details) {
      return error.details.find((d) =>
        d.toLowerCase().includes(field.toLowerCase()),
      );
    }
    return undefined;
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="flex flex-col gap-4 w-full max-w-2xl text-left"
    >
      {error && error.error !== "VALIDATION_ERROR" && (
        <div className="text-danger-400 text-sm p-2 border border-danger-400 rounded">
          {error.message ?? "An error occurred"}
        </div>
      )}

      <label>
        <div className="text-sm font-medium text-text mb-1">Brand *</div>
        <input
          type="text"
          value={brand}
          onChange={(e) => setBrand(e.target.value)}
          className="w-full px-3 py-2 border border-border rounded focus:outline-none focus:border-brand-300"
        />
        {(fieldErrors.brand || getApiFieldError("brand")) && (
          <div className="text-danger-400 text-xs mt-1">
            {fieldErrors.brand || getApiFieldError("brand")}
          </div>
        )}
      </label>

      <label>
        <div className="text-sm font-medium text-text mb-1">Type *</div>
        <select
          value={type}
          onChange={(e) => setType(e.target.value)}
          className="w-full px-3 py-2 border border-border rounded focus:outline-none focus:border-brand-300 bg-surface text-text"
        >
          <option value="">Select type…</option>
          {BIKE_TYPE_OPTIONS.map((opt) => (
            <option key={opt} value={opt}>
              {opt}
            </option>
          ))}
        </select>
        {(fieldErrors.type || getApiFieldError("type")) && (
          <div className="text-danger-400 text-xs mt-1">
            {fieldErrors.type || getApiFieldError("type")}
          </div>
        )}
      </label>

      <label>
        <div className="text-sm font-medium text-text mb-1">Colour *</div>
        <input
          type="text"
          value={colour}
          onChange={(e) => setColour(e.target.value)}
          className="w-full px-3 py-2 border border-border rounded focus:outline-none focus:border-brand-300"
        />
        {(fieldErrors.colour || getApiFieldError("colour")) && (
          <div className="text-danger-400 text-xs mt-1">
            {fieldErrors.colour || getApiFieldError("colour")}
          </div>
        )}
      </label>

      <BikeLocationPicker
        latitude={latitude}
        longitude={longitude}
        onChange={setPositionFromMap}
      />
      {(fieldErrors.latitude || getApiFieldError("latitude")) && (
        <div className="text-danger-400 text-xs -mt-2">
          {fieldErrors.latitude || getApiFieldError("latitude")}
        </div>
      )}
      {(fieldErrors.longitude || getApiFieldError("longitude")) && (
        <div className="text-danger-400 text-xs -mt-2">
          {fieldErrors.longitude || getApiFieldError("longitude")}
        </div>
      )}

      <label>
        <div className="text-sm font-medium text-text mb-1">Status *</div>
        <select
          value={state}
          onChange={(e) => setStatus(e.target.value)}
          className="w-full px-3 py-2 border border-border rounded focus:outline-none focus:border-brand-300 bg-surface text-text"
        >
          {BIKE_STATE_OPTIONS.map((opt) => (
            <option key={opt} value={opt}>
              {opt}
            </option>
          ))}
        </select>
      </label>

      <button
        type="submit"
        disabled={isPending}
        className={`px-5 py-2 bg-brand-500 text-white rounded hover:bg-brand-600 self-start ${isPending ? "opacity-70 cursor-not-allowed" : "cursor-pointer"}`}
      >
        {isPending ? "Saving..." : "Save"}
      </button>
    </form>
  );
}
