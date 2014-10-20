import json
import math

from cache import Cache

def compute_gradient_linear_regression(weights, features, label):
    scale = dotProduct(features, weights) - label
    gradient = {}
    increment(gradient, scale, features)
    return gradient

def increment(d1, scale, d2):
    """
    Implements d1 += scale * d2 for sparse vectors.
    @param dict d1: the feature vector which is mutated.
    @param float scale
    @param dict d2: a feature vector.
    """
    for f, v in d2.items():
        d1[f] = d1.get(f, 0) + v * scale

def dotProduct(d1, d2):
    """
    @param dict d1: a feature vector represented by a mapping from a feature (string) to a weight (float).
    @param dict d2: same as d1
    @return float: the dot product between d1 and d2
    """
    if len(d1) < len(d2):
        return dotProduct(d2, d1)
    else:
        return sum(d1.get(f, 0) * v for f, v in d2.items())

class SGDRunner(object):
    def run(self):
        self.load_data()
        print "Computing weights"
        weights = self.run_sgd(self.data, self.dev_movie_ids, compute_gradient_linear_regression)
        print "Computing errors"
        print "Standard error on test data is: %s" % (self.standard_error(self.data, self.test_movie_ids, weights))
        save_weights()

    def load_data(self):
        self.data = json.load(open('data/features.json'))
        self.dev_movie_ids = json.load(open('data/dev.json'))
        self.test_movie_ids = json.load(open('data/test.json'))

    def save_weights(self):
        WEIGHTS_PATH = os.path.join('data', 'weights.json')
        Cache.save_file(WEIGHTS_PATH, weights)

    def run_sgd(self, data, movie_ids, compute_gradient):
        self.normalize_features(data)

        num_iters = 100
        eta = 0.001
        weights = {}
        for iteration in range(num_iters):
            for movie_id in movie_ids:
                movie_id = str(movie_id)
                if movie_id not in data:
                    continue

                gradient = compute_gradient(weights, data[movie_id]['features'], data[movie_id]['rating'])
                increment(weights, -1 * eta, gradient)
            print "Standard error on dev data after iteration %s: %s" %(iteration, self.standard_error(data, movie_ids, weights))
        return weights

    def normalize_features(self, data):
        # First find max and min for each feature
        max_min = {}
        for movie_id, movie_info in data.items():
            for feature_name, feature_value in movie_info['features'].items():
                if feature_name in max_min:
                    if max_min[feature_name][0] < feature_value:
                        max_min[feature_name][0] = feature_value
                    if max_min[feature_name][1] > feature_value:
                        max_min[feature_name][1] = feature_value
                else:
                    max_min[feature_name] = [feature_value, feature_value]

        # Normalize features
        for movie_id, movie_info in data.items():
            for feature_name, feature_value in movie_info['features'].items():
                if max_min[feature_name][0] == max_min[feature_name][1]:
                    # max == min for this feature
                    movie_info['features'][feature_name] = 1
                else:
                    movie_info['features'][feature_name] = (feature_value - max_min[feature_name][1]) / float(max_min[feature_name][0] - max_min[feature_name][1])

    def standard_error(self, data, movie_ids, weights):
        count = 0
        sum_squared_error = 0
        for movie_id in movie_ids:
            movie_id = str(movie_id)
            if movie_id not in data:
                continue

            predicted_rating = dotProduct(weights, data[movie_id]['features'])
            actual_rating = data[movie_id]['rating']
            sum_squared_error += pow(predicted_rating - actual_rating, 2)
            count += 1

        return math.sqrt(sum_squared_error / count)

if __name__ == '__main__':
    SGDRunner().run()
