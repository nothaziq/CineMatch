import { useNavigate } from "react-router-dom";
import { MovieCard } from "../../../components/MovieCard";
import type { RecommendationOut } from "../../../types/api";
import { ExplanationBadge } from "./ExplanationBadge";

interface RecommendationCardProps {
  recommendation: RecommendationOut;
}

export function RecommendationCard({ recommendation }: RecommendationCardProps) {
  const navigate = useNavigate();

  return (
    <div>
      <MovieCard
        movie={recommendation.movie}
        onClick={(m) => navigate(`/movies/${m.movie_id}`)}
      />
      <div className="mt-1.5">
        <ExplanationBadge explanation={recommendation.explanation} />
      </div>
    </div>
  );
}
