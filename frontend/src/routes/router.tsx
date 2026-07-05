import { createBrowserRouter } from "react-router-dom";
import { AppLayout } from "../layouts/AppLayout";
import { FavoritesPage } from "../features/favorites/pages/FavoritesPage";
import { GenreDetailPage } from "../features/genres/pages/GenreDetailPage";
import { GenresPage } from "../features/genres/pages/GenresPage";
import { HomePage } from "../features/home/pages/HomePage";
import { MovieDetailPage } from "../features/movie/pages/MovieDetailPage";
import { RecommendationsPage } from "../features/recommendations/pages/RecommendationsPage";
import { SearchPage } from "../features/search/pages/SearchPage";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <AppLayout />,
    children: [
      { index: true, element: <HomePage /> },
      { path: "movies/:movieId", element: <MovieDetailPage /> },
      { path: "search", element: <SearchPage /> },
      { path: "recommendations", element: <RecommendationsPage /> },
      { path: "favorites", element: <FavoritesPage /> },
      { path: "genres", element: <GenresPage /> },
      { path: "genres/:genre", element: <GenreDetailPage /> },
    ],
  },
]);
