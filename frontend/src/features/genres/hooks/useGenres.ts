import { useQuery } from "@tanstack/react-query";
import { fetchGenres } from "../../movie/services/movieApi";

export function useGenres() {
  return useQuery({
    queryKey: ["genres"],
    queryFn: fetchGenres,
    staleTime: 10 * 60 * 1000, // genre list barely changes within a session
  });
}
