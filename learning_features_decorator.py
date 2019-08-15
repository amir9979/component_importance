from learning_classify import AbstractLearningClassify
from sklearn.feature_selection import VarianceThreshold


class AbstractFeatureDecorator(AbstractLearningClassify):
    def __init__(self, dir_id, learning_classify):
        super(AbstractFeatureDecorator, self).__init__(dir_id)
        self.learning_classify = learning_classify

    def get_learning_classify(self):
        return self.learning_classify


class TransformDecorator(AbstractFeatureDecorator):
    def __init__(self, dir_id, learning_classify, transformer):
        super(TransformDecorator, self).__init__(dir_id, learning_classify)
        self.transformer = transformer
        self.transformer.fit_transform(self.get_learning_classify().get_training_features(), self.get_learning_classify().get_training_labels())

    def _transform(self, features):
        return self.variance_threshold.transform(features)

    def get_training_features(self):
        return self._transform(self.get_learning_classify().get_training_features())

    def get_testing_features(self):
        return self._transform(self.get_learning_classify().get_testing_features())


def low_variance_decorator(dir_id, learning_classify, threshold=(.8 * (1 - .8))):
    return TransformDecorator(dir_id, learning_classify, VarianceThreshold(threshold=threshold))

def k_best():
    pass
