import { apiClient } from "../../../services/apiClient";
import type {
  GenreCount,
  MovieDetailOut,
  MovieOut,
  PaginatedMovies,
  RecommendationListOut,
} from "../../../types/api";

export type SortOption = "popularity" | "top_rated" | "recent" | "title";

export async function fetchMovies(params: {
  genre?: string;
  sort?: SortOption;
  page?: number;
  page_size?: number;
}): Promise<PaginatedMovies> {
  const { data } = await apiClient.get<PaginatedMovies>("/movies", { params });
  return data;
}

// Note: /movies/search takes a flat `limit` (max 50), not offset-based
// pagination. There's no cursor on the backend yet, so "load more" is
// implemented by re-requesting with a larger limit against the same
// (stable-ordered) query — see features/search/hooks/useSearch.ts.
export async function searchMovies(query: string, limit = 20): Promise<MovieOut[]> {
  if (!query.trim()) return [];
  const { data } = await apiClient.get<MovieOut[]>("/movies/search", {
    params: { q: query, limit },
  });
  return data;
}

export async function fetchMovieDetail(movieId: number): Promise<MovieDetailOut> {
  const { data } = await apiClient.get<MovieDetailOut>(`/movies/${movieId}`);
  return data;
}

export async function fetchGenres(): Promise<GenreCount[]> {
  const { data } = await apiClient.get<GenreCount[]>("/movies/genres");
  return data;
}

export async function fetchRecommendations(
  movieId: number,
  k = 10
): Promise<RecommendationListOut> {
  const { data } = await apiClient.get<RecommendationListOut>(`/recommendations/${movieId}`, {
    params: { k },
  });
  return data;
}

export async function fetchBatchRecommendations(
  movieIds: number[],
  k = 20
): Promise<RecommendationListOut> {
  const { data } = await apiClient.post<RecommendationListOut>("/recommendations/batch", {
    movie_ids: movieIds,
    k,
  });
  return data;
}
