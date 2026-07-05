export function MovieCardSkeleton() {
  return (
    <div className="w-full shrink-0 animate-pulse">
      <div className="glass aspect-[2/3] w-full rounded-xl bg-[var(--color-panel)]" />
      <div className="mt-2 h-3.5 w-3/4 rounded bg-[var(--color-panel)]" />
      <div className="mt-1.5 h-3 w-1/3 rounded bg-[var(--color-panel)]" />
    </div>
  );
}
