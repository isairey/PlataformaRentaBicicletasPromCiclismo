import { useState } from 'react';
import { Link } from 'react-router-dom';
import type { Competition } from '../types';
import CompetitionDeleteDialog from './CompetitionDeleteDialog';

interface CompetitionListProps {
  competitions?: Competition[];
  isLoading: boolean;
  isError: boolean;
  isAdmin: boolean;
}

export default function CompetitionList({ competitions, isLoading, isError, isAdmin }: CompetitionListProps) {
  const [deletingCompetition, setDeletingCompetition] = useState<Competition | null>(null);

  if (isLoading) {
    return <p className="text-text-muted">Loading competitions...</p>;
  }

  if (isError) {
    return <p className="text-danger-400">Failed to load competitions. Please try again.</p>;
  }

  if (competitions && competitions.length === 0) {
    return <p className="text-text-muted">No competitions found.</p>;
  }

  return (
    <>
      <table className="w-full border-collapse text-left text-sm">
        <thead>
          <tr className="border-b-2 border-border">
            <th className="px-3 py-2 text-text-muted font-medium">Name</th>
            <th className="px-3 py-2 text-text-muted font-medium">Type</th>
            <th className="px-3 py-2 text-text-muted font-medium">Start Date</th>
            <th className="px-3 py-2 text-text-muted font-medium">End Date</th>
            <th className="px-3 py-2 text-text-muted font-medium">Description</th>
            {isAdmin && <th className="px-3 py-2 text-text-muted font-medium">Actions</th>}
          </tr>
        </thead>
        <tbody>
          {competitions && competitions.map((competition) => (
            <tr key={competition.id} className="border-b border-border hover:bg-surface-muted">
              <td className="px-3 py-2 text-text">{competition.name}</td>
              <td className="px-3 py-2 text-text">{competition.type}</td>
              <td className="px-3 py-2 text-text">{competition.startDate}</td>
              <td className="px-3 py-2 text-text">{competition.endDate}</td>
              <td className="px-3 py-2 text-text">{competition.description}</td>
              {isAdmin && (
                <td className="px-3 py-2 flex gap-3">
                  <Link to={`/competitions/${competition.id}/edit`} className="text-brand-500 hover:text-brand-600">
                    Edit
                  </Link>
                  <button
                    onClick={() => setDeletingCompetition(competition)}
                    className="bg-transparent border-none text-danger-400 cursor-pointer p-0 hover:underline text-sm"
                  >
                    Delete
                  </button>
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>

      {deletingCompetition && (
        <CompetitionDeleteDialog
          competitionId={deletingCompetition.id}
          competitionName={deletingCompetition.name}
          isOpen={true}
          onClose={() => setDeletingCompetition(null)}
        />
      )}
    </>
  );
}
