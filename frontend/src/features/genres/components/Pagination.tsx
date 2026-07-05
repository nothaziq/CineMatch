import { ChevronLeft, ChevronRight } from "lucide-react";

interface PaginationProps {
  page: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}

export function Pagination({ page, totalPages, onPageChange }: PaginationProps) {
  if (totalPages <= 1) return null;

  return (
    <div className="flex items-center justify-center gap-4 py-8">
      <button
        onClick={() => onPageChange(page - 1)}
        disabled={page <= 1}
        aria-label="Previous page"
        className="glass flex h-9 w-9 items-center justify-center rounded-full text-[var(--color-bone)] transition-colors hover:border-[var(--color-marquee)] disabled:cursor-not-allowed disabled:opacity-30"
      >
        <ChevronLeft size={18} />
      </button>

      <span className="font-[var(--font-mono)] text-sm text-[var(--color-bone-dim)]">
        Page {page} of {totalPages}
      </span>

      <button
        onClick={() => onPageChange(page + 1)}
        disabled={page >= totalPages}
        aria-label="Next page"
        className="glass flex h-9 w-9 items-center justify-center rounded-full text-[var(--color-bone)] transition-colors hover:border-[var(--color-marquee)] disabled:cursor-not-allowed disabled:opacity-30"
      >
        <ChevronRight size={18} />
      </button>
    </div>
  );
}
