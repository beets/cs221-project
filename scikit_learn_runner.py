import json
import os
import helpers
from sklearn import linear_model
from cache import Cache
import logging
import sys
import time

class ScikitLearnRunner(object):
    def run(self):
        self.load_data()

        self.run_model(linear_model.LinearRegression(), "linear regression")

    def load_data(self):
        self.data = json.load(open('data/features.json'))
        helpers.normalize_features(self.data)

        self.dev_movie_ids = json.load(open('data/dev.json'))
        self.test_movie_ids = json.load(open('data/test.json'))

        # Transforms the data so they can be used by scikit-learn library.
        self.data_transformer = helpers.DataTransformer(self.data, self.dev_movie_ids)
        self.training_feature_matrix, self.training_labels = self.data_transformer.get_training_data()

        self.predict_feature_matrix, self.predict_labels, self.predict_ids = \
            self.data_transformer.transform_movies_data(self.data, self.test_movie_ids)

    def run_model(self, model, model_name):
        logging.info("Fitting model %s..." % model_name)
        start = time.time()
        model.fit(self.training_feature_matrix, self.training_labels)
        logging.info("Fitting model %s done! Took %s seconds." % (model_name, time.time() - start))

        logging.info("Predicting using model %s..." % model_name)
        start = time.time()
        predictions = model.predict(self.predict_feature_matrix)
        logging.info("Predicting using model %s done! Took %s seconds." % (model_name, time.time() - start))

        helpers.standard_eror(predictions, self.predict_labels)

if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    ScikitLearnRunner().run()
