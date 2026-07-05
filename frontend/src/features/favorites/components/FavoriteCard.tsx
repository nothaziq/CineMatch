import { X } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { MovieCard } from "../../../components/MovieCard";
import type { MovieOut } from "../../../types/api";

interface FavoriteCardProps {
  movie: MovieOut;
  onRemove: (movieId: number) => void;
}

export function FavoriteCard({ movie, onRemove }: FavoriteCardProps) {
  const navigate = useNavigate();

  return (
    <div className="relative">
      <MovieCard movie={movie} onClick={(m) => navigate(`/movies/${m.movie_id}`)} />
      {/* Sibling button positioned over the card, not nested inside
          MovieCard's own <button> — nesting buttons is invalid HTML and
          makes click behavior unreliable. */}
      <button
        onClick={() => onRemove(movie.movie_id)}
        aria-label={`Remove ${movie.title} from favorites`}
        className="glass absolute right-2 top-2 z-10 flex h-8 w-8 items-center justify-center rounded-full text-[var(--color-bone-dim)] transition-colors hover:text-[var(--color-marquee)]"
      >
        <X size={16} />
      </button>
    </div>
  );
}
