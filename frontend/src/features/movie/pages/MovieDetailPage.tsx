import { useParams } from "react-router-dom";
import { useMovieDetail, useSimilarMovies } from "../hooks/useMovieDetail";
import { MovieHero } from "../components/MovieHero";
import { SimilarMoviesRail } from "../components/SimilarMoviesRail";

export function MovieDetailPage() {
  const { movieId } = useParams<{ movieId: string }>();
  const parsedId = movieId ? Number(movieId) : undefined;
  const isValidId = parsedId !== undefined && Number.isInteger(parsedId);

  const detail = useMovieDetail(isValidId ? parsedId : undefined);
  const similar = useSimilarMovies(isValidId ? parsedId : undefined);

  if (!isValidId) {
    return <NotFoundState message="That doesn't look like a valid movie link." />;
  }

  if (detail.isLoading) {
    return <MovieDetailSkeleton />;
  }

  if (detail.isError || !detail.data) {
    const status = (detail.error as any)?.response?.status;
    if (status === 404) {
      return <NotFoundState message="We couldn't find that movie." />;
    }
    return <NotFoundState message="Something went wrong loading this movie. Try again." />;
  }

  return (
    <div>
      <MovieHero movie={detail.data} />
      <SimilarMoviesRail
        recommendations={similar.data?.recommendations}
        isLoading={similar.isLoading}
        isError={similar.isError}
      />
    </div>
  );
}

function NotFoundState({ message }: { message: string }) {
  return (
    <div className="flex min-h-[50vh] flex-col items-center justify-center gap-2 px-6 text-center">
      <p className="font-[var(--font-display)] text-2xl text-[var(--color-bone)]">{message}</p>
      <p className="text-sm text-[var(--color-bone-dim)]">
        Try going back to browse something else.
      </p>
    </div>
  );
}

function MovieDetailSkeleton() {
  return (
    <div className="animate-pulse px-6 py-12 md:px-10">
      <div className="flex flex-col gap-8 md:flex-row">
        <div className="glass mx-auto h-72 w-48 rounded-xl bg-[var(--color-panel)] md:mx-0" />
        <div className="flex-1 space-y-4">
          <div className="h-10 w-2/3 rounded bg-[var(--color-panel)]" />
          <div className="h-4 w-1/3 rounded bg-[var(--color-panel)]" />
          <div className="h-20 w-full max-w-2xl rounded bg-[var(--color-panel)]" />
        </div>
      </div>
    </div>
  );
}
