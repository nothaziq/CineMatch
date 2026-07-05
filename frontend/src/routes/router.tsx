import { createBrowserRouter } from "react-router-dom";
import { AppLayout } from "../layouts/AppLayout";
import { HomePage } from "../features/home/pages/HomePage";
import { MovieDetailPage } from "../features/movie/pages/MovieDetailPage";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <AppLayout />,
    children: [
      { index: true, element: <HomePage /> },
      { path: "movies/:movieId", element: <MovieDetailPage /> },
      // Search, Recommendations flow, Favorites, Genres pages plug in here
      // as their own routes as we build each feature next.
    ],
  },
]);
