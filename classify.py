import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import KFold
from sklearn.cross_validation import cross_val_score, cross_val_predict
from sklearn import metrics
from numpy import interp
# import matplotlib.pyplot as plt
import re
import argparse



features = pd.read_csv(r"C:\amirelm\component_importnace\data\d4j_lang10\training_set\19")
# features.describe()
test_names = np.array(features['test_name'])
function_names = np.array(features['test_name'])
labels = np.array(features['label'])
features = features.drop('test_name', axis=1)
features = features.drop('function_name', axis=1)
features = features.drop('label', axis=1)
feature_list = list(features.columns)
features = np.array(features)

train_features, test_features, train_labels, test_labels = train_test_split(features, labels, test_size=0.2, random_state=42)
rf = RandomForestClassifier(n_estimators=1000, random_state=42)
model = rf.fit(train_features, train_labels)
prediction_probabilities = rf.predict_proba(test_features)
predictions = rf.predict(test_features)


importances = list(rf.feature_importances_)
feature_importances = [(feature, round(importance, 2)) for feature, importance in zip(feature_list, importances)]
feature_importances = sorted(feature_importances, key = lambda x: x[1], reverse = True)



kf = KFold(n_splits=10) # Define the split - into 2 folds
kf.get_n_splits(features) # returns the number of splitting iterations in the cross-validator
print(kf)
KFold(n_splits=10, random_state=None, shuffle=False)
for train_index, test_index in kf.split(X):
    X_train, X_test = X[train_index], X[test_index]
    y_train, y_test = y[train_index], y[test_index]

scores = cross_val_score(model, features, labels, cv=10)

predictions = cross_val_predict(model, features, labels, cv=10)
accuracy = metrics.r2_score(labels, predictions)

from sklearn.metrics import average_precision_score
average_precision = average_precision_score(test_labels, classifier.decision_function(test_features))

print('Average precision-recall score: {0:0.2f}'.format(
      average_precision))

def calc_pr_metrics(truth_df, score_df):
    recall_array = np.linspace(0, 1, 100)
    p, r, thresh = metrics.precision_recall_curve(truth_df, score_df)
    p, r, thresh = p[::-1], r[::-1], thresh[::-1]  # reverse order of results
    thresh = np.insert(thresh, 0, 1.0)
    precision_array = interp(recall_array, r, p)
    threshold_array = interp(recall_array, r, thresh)
    pr_auc = metrics.auc(recall_array, precision_array)
    return precision_array, recall_array, pr_auc






