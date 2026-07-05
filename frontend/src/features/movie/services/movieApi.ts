import { apiClient } from "../../../services/apiClient";
import type { MovieDetailOut, PaginatedMovies, RecommendationListOut } from "../../../types/api";

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

export async function fetchMovieDetail(movieId: number): Promise<MovieDetailOut> {
  const { data } = await apiClient.get<MovieDetailOut>(`/movies/${movieId}`);
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
