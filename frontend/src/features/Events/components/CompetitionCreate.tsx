import { Link } from 'react-router-dom';
import useCreateCompetition from '../hooks/useCreateCompetition';
import CompetitionForm from './CompetitionForm';
import type { ApiError } from '../../../types';

export default function CompetitionCreate() {
  const mutation = useCreateCompetition();

  return (
    <div>
      <h1 className="text-2xl font-semibold text-text mb-6">Add Competition</h1>
      <CompetitionForm
        onSubmit={(payload) => mutation.mutate(payload)}
        isPending={mutation.isPending}
        error={mutation.error as ApiError | null}
      />
      <p className="mt-4">
        <Link to="/competitions" className="text-brand-500 hover:text-brand-600 text-sm">&larr; Cancel</Link>
      </p>
    </div>
  );
}
