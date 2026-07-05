import { useQuery } from "@tanstack/react-query";
import { fetchMovies, type SortOption } from "../../movie/services/movieApi";

export function useGenreMovies(genre: string, sort: SortOption, page: number) {
  return useQuery({
    queryKey: ["movies", "genre", genre, sort, page],
    queryFn: () => fetchMovies({ genre, sort, page, page_size: 24 }),
    placeholderData: (previous) => previous, // keep the grid steady while paging/re-sorting
  });
}
