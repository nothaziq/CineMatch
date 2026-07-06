// Mirrors backend/app/schemas/movie.py and recommendation.py field-for-field.
// Keep these in sync manually for now — a future step could generate them
// from the OpenAPI schema FastAPI already produces at /openapi.json.

export interface MovieOut {
  movie_id: number;
  title: string;
  year: number | null;
  genres: string[];
  avg_rating: number;
  rating_count: number;
  poster_url: string | null;
}

export interface MovieDetailOut extends MovieOut {
  overview: string;
  director: string;
  cast: string[];
  keywords: string[];
  production_companies: string[];
  runtime: number | null;
  release_date: string | null;
  backdrop_url: string | null;
  trailer_url: string | null;
  tmdb_id: number | null;
  imdb_id: string | null;
}

export interface PaginatedMovies {
  items: MovieOut[];
  page: number;
  page_size: number;
  total_items: number;
  total_pages: number;
}

export interface GenreCount {
  genre: string;
  count: number;
}

export interface RecommendationOut {
  movie: MovieOut;
  score: number;
  explanation: string;
}

export interface RecommendationListOut {
  seed_movie_ids: number[];
  recommendations: RecommendationOut[];
}

export interface ApiError {
  error: {
    code: string;
    message: string;
    status: number;
  };
}
