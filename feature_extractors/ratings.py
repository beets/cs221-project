from feature_extractor_base import Base
from helpers import encode
from models.info_type import RATING_ID

import logging

class RatingsFeatureExtractor(Base):
    oracle = True

    def get_ratings(self):
        return self.session.query(
            self.models.MovieInfoIDX.movie_id,
            self.models.MovieInfoIDX.info
        ).filter(
            self.models.MovieInfoIDX.movie_id.in_(self.movie_ids),
            self.models.MovieInfoIDX.info_type_id.in_([RATING_ID]),
        ).distinct(
            self.models.MovieInfoIDX.movie_id
        )

    def extract(self):
        features = {}
        for movie_id, ratings in self.get_ratings():
            if features.get(movie_id) is None:
                features[movie_id] = {}
            features[movie_id]['ratings'] = float(ratings)
            logging.debug("Extracted ratings: %s %s" % (movie_id, ratings))
        return features
