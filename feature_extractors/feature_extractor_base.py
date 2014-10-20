import os
from collections import defaultdict

from cache import Cache
from session import session
import models


class Base(object):
    # Override this when you're developing
    __cache__ = True

    # Override if it shouldn't be in the oracle, or should be in the baseline.
    oracle = False
    baseline = True

    def __init__(self, movie_ids):
        self.session = session
        self.models = models
        self.movie_ids = movie_ids

    def extract_cached(self):
        cache_file = os.path.join('data', 'cache', '%s.json' % (self.__class__.__name__))
        return Cache.cache(self.__cache__, cache_file, self.extract)

    # This is the only required method
    # It should return a hash with keys that are movie ids, and values that
    # are hashes of features
    def extract(self):
        raise NotImplementedError

    def segmented_movie_ids(self, segment_size=500):
        """Yield movie ids in chunks"""
        tmp_movie_ids = []
        for movie_id in self.movie_ids:
            tmp_movie_ids.append(movie_id)
            if len(tmp_movie_ids) == segment_size:
                yield tmp_movie_ids
                tmp_movie_ids = []
        if len(tmp_movie_ids) > 0:
            yield tmp_movie_ids

    def movies_query(self):
        return self.session.query(
            self.models.Movie
        ).filter(
            self.models.Movie.id.in_(self.movie_ids)
        )

    def with_appearances(self, iter, min_appearances, count_of, appears_in):
        """Use this method to count the number of appearances the count_of
        appears in appears_in, removing entries that don't appear at least
        min_appearances times.

        count_of - this should be a lambda to pull an identifier out of each
            item of the iterator
        appears_in - this should be a lambda used to pull what the count_of
            appeared in for each item of the iterator
        """
        appearances = defaultdict(set)
        iter = list(iter)
        for item in iter:
            appearances[count_of(item)].add(appears_in(item))

        for item in iter:
            length = len(appearances[count_of(item)])
            if length >= min_appearances:
                yield tuple(list(item) + [length])
