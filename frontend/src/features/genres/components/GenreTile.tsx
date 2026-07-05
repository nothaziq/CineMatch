import { Link } from "react-router-dom";
import type { GenreCount } from "../../../types/api";

interface GenreTileProps {
  genre: GenreCount;
}

export function GenreTile({ genre }: GenreTileProps) {
  return (
    <Link
      to={`/genres/${encodeURIComponent(genre.genre)}`}
      className="light-leak glass group flex flex-col justify-between rounded-xl px-5 py-6 transition-transform duration-300 ease-out hover:-translate-y-1 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--color-signal)]"
    >
      <span className="font-[var(--font-display)] text-lg font-semibold text-[var(--color-bone)]">
        {genre.genre}
      </span>
      <span className="mt-3 font-[var(--font-mono)] text-xs text-[var(--color-bone-dim)]">
        {genre.count.toLocaleString()} movie{genre.count === 1 ? "" : "s"}
      </span>
    </Link>
  );
}
