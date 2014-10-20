from feature_extractor_base import Base
from helpers import encode
from models.info_type import GROSS_ID

import logging
import re

GROSS_RE = "\$(\d+) \(USA\)"

class GrossFeatureExtractor(Base):
    oracle = True

    def get_gross(self):
        return self.session.query(
            self.models.MovieInfo.movie_id,
            self.models.MovieInfo.info
        ).filter(
            self.models.MovieInfo.movie_id.in_(self.movie_ids),
            self.models.MovieInfo.info_type_id.in_([GROSS_ID]),
        )

    def extract(self):
        features = {}
        for movie_id, gross in self.get_gross():
            gross = gross.replace(",", "")
            match = re.match(GROSS_RE, gross)
            if not match or match.lastindex != 1:
                logging.debug("Skipping gross: %s" % gross)
                continue

            gross_int = 0
            try:
                gross_int = int(match.group(1))
                logging.debug("Extracted Gross: %s %s -> %d" % (movie_id, gross, gross_int))
            except:
                logging.debug("Error parsing gross: %s" % gross)
                continue
                
            if features.get(movie_id) is None:
                features[movie_id] = {}
            features[movie_id]['gross'] = gross_int
        return features
