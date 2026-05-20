import useDeleteBike from '../hooks/useDeleteBike';

interface BikeDeleteDialogProps {
  bikeId: string;
  bikeName: string;
  isOpen: boolean;
  onClose: () => void;
}

export default function BikeDeleteDialog({ bikeId, bikeName, isOpen, onClose }: BikeDeleteDialogProps) {
  const mutation = useDeleteBike();

  if (!isOpen) return null;

  function handleConfirm() {
    mutation.mutate(bikeId, {
      onSuccess: () => onClose(),
    });
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-surface rounded-lg p-6 w-full max-w-sm shadow-lg">
        <h2 className="text-lg font-semibold text-text mb-2">Delete Bike</h2>
        <p className="text-text-muted text-sm">Are you sure you want to delete &quot;{bikeName}&quot;?</p>
        <div className="flex gap-2 justify-end mt-4">
          <button
            onClick={onClose}
            disabled={mutation.isPending}
            className="px-4 py-2 border border-border rounded text-text-muted hover:bg-surface-muted disabled:opacity-70 cursor-pointer bg-transparent"
          >
            Cancel
          </button>
          <button
            onClick={handleConfirm}
            disabled={mutation.isPending}
            className={`px-4 py-2 bg-danger-400 text-white rounded hover:bg-red-500 ${mutation.isPending ? 'opacity-70 cursor-not-allowed' : 'cursor-pointer'}`}
          >
            {mutation.isPending ? 'Deleting...' : 'Confirm Delete'}
          </button>
        </div>
      </div>
    </div>
  );
}
