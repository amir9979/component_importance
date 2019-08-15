from influence_classify import InfluenceClassify
from random import random
import json


class SanityClassify(InfluenceClassify):
    NOISE = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    INFLUENCE_VALUE = {True: {True: 1, False: 0.001}, False: {True: 1, False: 1}}

    def __init__(self, dir_id, noise):
        super(SanityClassify, self).__init__(dir_id)
        self.name = "sanity_{0}".format(noise)
        self.noise = noise
        self.bugs = json.loads(self.get_dir_id().read_file("bugs"))
        self.traces = json.loads(self.get_dir_id().read_file("traces_json"))
        self.tests_results = json.loads(self.get_dir_id().read_file("tests_results"))

    def get_influence_value(self, is_buggy, is_test_pass):
        noise = self.noise
        influence = SanityClassify.INFLUENCE_VALUE[is_buggy][is_test_pass]
        if influence == 1:
            return max(influence - noise, 0.001)
        return min(influence + noise, 1)

    def get_influence(self):
        influence_matrix = dict()
        for test in self.traces:
            influence_matrix[test] = dict()
            for component in self.traces[test]:
                influence_matrix[test][component] = self.get_influence_value(
                    component in self.bugs, self.tests_results[test])
        return influence_matrix

    def get_name(self):
        return self.name

    @staticmethod
    def get_all_sanity_classifers(dir_id):
        return map(lambda noise: SanityClassify(dir_id, noise), SanityClassify.NOISE)
