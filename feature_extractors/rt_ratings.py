import logging

from feature_extractor_base import Base
from helpers import encode


class RtRatingsFeatureExtractor(Base):
    oracle = True

    def get_ratings(self):
        return self.session.query(
            self.models.RtRatings.imdb_movie_id,
            self.models.RtRatings.critics_score,
            self.models.RtRatings.critics_rating,
            self.models.RtRatings.audience_score,
            self.models.RtRatings.audience_rating
        ).filter(
            self.models.RtRatings.imdb_movie_id.in_(self.movie_ids)
        )

    def extract(self):
        features = {}
        for movie_id, critics_score, critics_rating, audience_score, audience_rating in self.get_ratings():
            logging.debug(
                "Extracted RT rating: %d %d %s %d %s" %
                (movie_id, critics_score, critics_rating, audience_score, audience_rating)
            )
            if features.get(movie_id) is None:
                features[movie_id] = {}
            if critics_score > 0:
                features[movie_id]['rt_critics_score'] = critics_score
            if critics_rating != '0':
                features[movie_id]['rt_critics_rating_' + critics_rating] = 1
            if audience_score > 0:
                features[movie_id]['rt_audience_score'] = audience_score
            if audience_rating != '0':
                features[movie_id]['rt_audience_rating_' + audience_rating] = 1
        return features
