interface ReturnConfirmDialogProps {
  rentalId: string;
  bikeId: string;
  isOpen: boolean;
  isPending: boolean;
  errorMessage?: string;
  onConfirm: () => void;
  onCancel: () => void;
}

export default function ReturnConfirmDialog({
  bikeId,
  isOpen,
  isPending,
  errorMessage,
  onConfirm,
  onCancel,
}: ReturnConfirmDialogProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[1000] flex items-center justify-center bg-black/40">
      <div className="bg-surface border border-border rounded-lg shadow-lg w-full max-w-sm p-6 flex flex-col gap-4">
        <h2 className="text-lg font-semibold text-text">Return Bike</h2>
        <p className="text-sm text-text-muted">
          Return bike <span className="font-mono text-text">{bikeId.slice(0, 8)}…</span>?
        </p>
        {errorMessage && (
          <p className="text-sm text-danger-400">{errorMessage}</p>
        )}
        <div className="flex gap-3 justify-end">
          <button
            className="px-4 py-2 text-sm rounded border border-border text-text hover:bg-surface-alt disabled:opacity-50"
            onClick={onCancel}
            disabled={isPending}
          >
            Cancel
          </button>
          <button
            className="px-4 py-2 text-sm rounded bg-danger-400 text-white hover:bg-danger-500 disabled:opacity-50"
            onClick={onConfirm}
            disabled={isPending}
          >
            {isPending ? 'Returning…' : 'Confirm Return'}
          </button>
        </div>
      </div>
    </div>
  );
}
