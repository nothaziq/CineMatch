import { useNavigate } from "react-router-dom";
import { MovieRail } from "../../../components/MovieRail";
import type { MovieOut } from "../../../types/api";
import { HeroSection } from "../components/HeroSection";
import { useRecentMovies, useTopRatedMovies, useTrendingMovies } from "../hooks/useHomeData";

export function HomePage() {
  const navigate = useNavigate();
  const trending = useTrendingMovies();
  const topRated = useTopRatedMovies();
  const recent = useRecentMovies();

  const goToMovie = (movie: MovieOut) => navigate(`/movies/${movie.movie_id}`);

  return (
    <div>
      <HeroSection />
      <MovieRail
        title="Trending Now"
        movies={trending.data?.items}
        isLoading={trending.isLoading}
        isError={trending.isError}
        onSelectMovie={goToMovie}
      />
      <MovieRail
        title="Top Rated"
        movies={topRated.data?.items}
        isLoading={topRated.isLoading}
        isError={topRated.isError}
        onSelectMovie={goToMovie}
      />
      <MovieRail
        title="Recently Added"
        movies={recent.data?.items}
        isLoading={recent.isLoading}
        isError={recent.isError}
        onSelectMovie={goToMovie}
      />
    </div>
  );
}
