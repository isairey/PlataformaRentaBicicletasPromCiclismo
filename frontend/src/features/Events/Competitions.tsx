import { Link } from 'react-router-dom';
import useFetchCompetitions from './hooks/useFetchCompetitions';
import CompetitionList from './components/CompetitionList';
import { useAuth } from '../../services/useAuth';

export default function Competitions() {
  const { data, isLoading, isError } = useFetchCompetitions();
  const { isAdmin } = useAuth();

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-semibold text-text">Competitions</h1>
        {isAdmin && (
          <Link
            to="/competitions/new"
            className="px-5 py-2 bg-brand-500 text-white rounded hover:bg-brand-600 no-underline text-sm"
          >
            Add Competition
          </Link>
        )}
      </div>
      <CompetitionList competitions={data} isLoading={isLoading} isError={isError} isAdmin={isAdmin} />
    </div>
  );
}
