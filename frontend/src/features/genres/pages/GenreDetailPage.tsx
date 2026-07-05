import { useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { ChevronLeft } from "lucide-react";
import { MovieCard } from "../../../components/MovieCard";
import { MovieCardSkeleton } from "../../../components/MovieCardSkeleton";
import type { MovieOut } from "../../../types/api";
import type { SortOption } from "../../movie/services/movieApi";
import { Pagination } from "../components/Pagination";
import { SortSelect } from "../components/SortSelect";
import { useGenreMovies } from "../hooks/useGenreMovies";

export function GenreDetailPage() {
  const { genre } = useParams<{ genre: string }>();
  const decodedGenre = genre ? decodeURIComponent(genre) : "";
  const navigate = useNavigate();

  const [sort, setSort] = useState<SortOption>("popularity");
  const [page, setPage] = useState(1);

  const { data, isLoading, isFetching, isError } = useGenreMovies(decodedGenre, sort, page);

  const goToMovie = (movie: MovieOut) => navigate(`/movies/${movie.movie_id}`);

  function handleSortChange(next: SortOption) {
    setSort(next);
    setPage(1); // re-sorting starts back at page 1
  }

  if (!decodedGenre) {
    return (
      <p className="px-6 py-10 text-center text-sm text-[var(--color-bone-dim)] md:px-10">
        That doesn't look like a valid genre.
      </p>
    );
  }

  return (
    <div className="px-6 py-10 md:px-10">
      <Link
        to="/genres"
        className="mb-4 inline-flex items-center gap-1 text-sm text-[var(--color-bone-dim)] transition-colors hover:text-[var(--color-bone)]"
      >
        <ChevronLeft size={16} />
        All genres
      </Link>

      <div className="mb-8 flex flex-wrap items-center justify-between gap-4">
        <h1 className="font-[var(--font-display)] text-3xl font-semibold text-[var(--color-bone)]">
          {decodedGenre}
          {data && (
            <span className="ml-3 font-[var(--font-mono)] text-base font-normal text-[var(--color-bone-dim)]">
              {data.total_items.toLocaleString()} movies
            </span>
          )}
        </h1>
        <SortSelect value={sort} onChange={handleSortChange} />
      </div>

      {isError && (
        <p className="text-sm text-[var(--color-bone-dim)]">
          Couldn't load this genre right now. Try refreshing.
        </p>
      )}

      {isLoading && (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
          {Array.from({ length: 12 }).map((_, i) => (
            <MovieCardSkeleton key={i} />
          ))}
        </div>
      )}

      {!isLoading && !isError && data && (
        <>
          {data.items.length === 0 ? (
            <p className="py-10 text-center text-sm text-[var(--color-bone-dim)]">
              No movies found in this genre.
            </p>
          ) : (
            <div
              className={`grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 ${
                isFetching ? "opacity-60 transition-opacity" : ""
              }`}
            >
              {data.items.map((movie) => (
                <MovieCard key={movie.movie_id} movie={movie} onClick={goToMovie} />
              ))}
            </div>
          )}

          <Pagination page={data.page} totalPages={data.total_pages} onPageChange={setPage} />
        </>
      )}
    </div>
  );
}
