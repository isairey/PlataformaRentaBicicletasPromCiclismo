import { useParams, Link } from 'react-router-dom';
import useFetchCompetitions from '../hooks/useFetchCompetitions';
import useUpdateCompetition from '../hooks/useUpdateCompetition';
import CompetitionForm from './CompetitionForm';
import type { ApiError } from '../../../types';

export default function CompetitionEdit() {
  const { id } = useParams<{ id: string }>();
  const competitionId = Number(id);
  const { data: competitions, isLoading, isError } = useFetchCompetitions();
  const competition = competitions?.find((c) => c.id === competitionId);
  const mutation = useUpdateCompetition(competitionId);

  if (isLoading) {
    return <p className="text-text-muted">Loading competition...</p>;
  }

  if (isError || !competition) {
    return (
      <div>
        <p className="text-text mb-2">Competition not found.</p>
        <Link to="/competitions" className="text-brand-500 hover:text-brand-600 text-sm">&larr; Back to Competitions</Link>
      </div>
    );
  }

  return (
    <div>
      <h1 className="text-2xl font-semibold text-text mb-6">Edit Competition</h1>
      <CompetitionForm
        key={competition.id}
        defaultValues={competition}
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
