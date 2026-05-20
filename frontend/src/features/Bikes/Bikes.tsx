import { Link } from "react-router-dom";
import useFetchBikes from "./hooks/useFetchBikes";
import BikeList from "./components/BikeList";

export default function Bikes() {
  const { data, isLoading, isError } = useFetchBikes();

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-semibold text-text">Bikes</h1>
        <Link
          to="/bikes/new"
          className="px-5 py-2 bg-brand-500 text-white rounded hover:bg-brand-600 no-underline text-sm"
        >
          Add Bike
        </Link>
      </div>
      <BikeList bikeData={data} isLoading={isLoading} isError={isError} />
    </div>
  );
}
