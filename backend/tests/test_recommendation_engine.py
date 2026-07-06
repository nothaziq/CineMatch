from __future__ import annotations


class TestRecommend:
    def test_excludes_the_seed_movie_itself(self, built_movie_repository):
        recs = built_movie_repository.recommender.recommend(1, k=5)
        assert all(r.movie_id != 1 for r in recs)

    def test_respects_k_limit(self, built_movie_repository):
        recs = built_movie_repository.recommender.recommend(1, k=2)
        assert len(recs) <= 2

    def test_similar_genre_movies_rank_above_dissimilar_ones(self, built_movie_repository):
        """Movies 1 and 2 are both Action/Sci-Fi 'Galaxy Raiders' entries;
        movie 3 is Romance/Drama. Movie 2 should rank above movie 3 when
        recommending from movie 1."""
        recs = built_movie_repository.recommender.recommend(1, k=10)
        scores_by_id = {r.movie_id: r.score for r in recs}
        assert scores_by_id[2] > scores_by_id[3]

    def test_shared_genre_appears_in_explanation_features(self, built_movie_repository):
        recs = built_movie_repository.recommender.recommend(1, k=10)
        rec_for_2 = next(r for r in recs if r.movie_id == 2)
        assert "Sci-Fi" in rec_for_2.shared_features or "Action" in rec_for_2.shared_features

    def test_unknown_movie_id_returns_empty(self, built_movie_repository):
        assert built_movie_repository.recommender.recommend(9999, k=5) == []


class TestRecommendForMultiple:
    def test_excludes_all_seed_movies(self, built_movie_repository):
        recs = built_movie_repository.recommender.recommend_for_multiple([1, 2], k=10)
        assert all(r.movie_id not in (1, 2) for r in recs)

    def test_respects_k_limit(self, built_movie_repository):
        recs = built_movie_repository.recommender.recommend_for_multiple([1, 2], k=1)
        assert len(recs) <= 1

    def test_results_sorted_descending_by_score(self, built_movie_repository):
        recs = built_movie_repository.recommender.recommend_for_multiple([1, 3], k=10)
        scores = [r.score for r in recs]
        assert scores == sorted(scores, reverse=True)
