from dir_structure import DirStructure, DirId
import json
import os
import networkx
import difflib
import textdistance
from html.parser import HTMLParser
# import nltk
import string
from collections import Counter
# from nltk.corpus import stopwords
import re
import sys
import time
import csv
import math
import numpy as np
from itertools import chain
from itertools import chain, combinations

# nltk.download('stopwords')
# nltk.download('punkt') # if necessary...


class MLStripper(HTMLParser):
    def __init__(self):
        super(MLStripper, self).__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)

    @staticmethod
    def strip_tags(html):
        s = MLStripper()
        s.feed(html)
        return s.get_data()


class FeatureExtraction(object):
    def __init__(self, dir_id):
        self.dir_id = dir_id
        self.labeled_features = dict()
        self.unlabeled_features = dict()

    def extract_labeled_data(self):
        if not os.path.exists(self.dir_id.mark):
            return
        with open(self.dir_id.labels) as f:
            labels = json.load(f)
        for test in labels:
            for function in labels[test]:
                features_dict = self.labeled_features.setdefault(test, dict()).setdefault(function, dict())
                features_dict['label'] = labels[test][function]
                features_dict.update(InstanceFeatureExtraction(self.dir_id, test, function).extract())
        with open(self.dir_id.labeled_data, "w") as f:
            json.dump(self.labeled_features, f)

    def extract_all_data(self):
        if not os.path.exists(self.dir_id.mark):
            return
        with open(self.dir_id.traces_json) as f:
            traces = json.load(f)
        for test in traces:
            for function in traces[test]:
                print(test, function, time.time())
                features_dict = self.unlabeled_features.setdefault(test, dict()).setdefault(function, dict())
                features_dict.update(InstanceFeatureExtraction(self.dir_id, test, function).extract())
        with open(self.dir_id.unlabeled_data, "w") as f:
            json.dump(self.unlabeled_features, f)

    def extract(self):
        self.extract_labeled_data()
        self.extract_all_data()
        self.get_testing_set()

    def get_training_set(self):
        csv_data = []
        features_header_added = False
        for matrix_id in os.listdir(self.dir_id.dir_structure.mark):
            dir_id = DirId(self.dir_id.dir_structure, matrix_id)
            if not os.path.exists(dir_id.labeled_data):
                print(f"{dir_id.labeled_data} is not exists")
                continue
            with open(dir_id.labeled_data) as f:
                data = json.loads(f.read())
            csv_data.extend(self.get_features(data, features_header_added))
            features_header_added = True
        with open(self.dir_id.training_set, "w") as f:
            csv.writer(f).writerows(csv_data)

    def get_features(self, data, features_header_added):
        csv_data = []
        for test in data:
            for function in data[test]:
                features_header = sorted(data[test][function].keys())
                if not features_header_added:
                    csv_data.append(["test_name", "function_name"] + features_header)
                    features_header_added = True
                csv_data.append([test, function] + list(map(data[test][function].get, features_header)))
        return csv_data

    def get_testing_set(self):
        with open(self.dir_id.unlabeled_data) as f:
            data = json.loads(f.read())
        csv_data = self.get_features(data, False)
        with open(self.dir_id.testing_set, "w") as f:
            csv.writer(f).writerows(csv_data)


class InstanceFeatureExtraction(object):
    def __init__(self, dir_id, test, function):
        self.dir_id = dir_id
        self.test = test
        self.function = function
        self.features = dict()

    def extract(self):
        self.call_graph()
        self.execution_graph()
        self.semantic_name()
        # self.javadoc()
        # self.commits_data()
        return self.features

    def _graph(self, g, graph_name):
        def find_node(name, nodes):
            return list(filter(lambda node: name in node.lower().replace("java.lang.", "").replace("java.io.", "").replace("java.util.", ""), nodes))
        test_node = find_node(self.test, g.nodes)
        component_node = find_node(self.function, g.nodes)
        if len(test_node) == 0 or len(component_node) == 0:
            return
        test_node = test_node[0]
        component_node = component_node[0]
        self.features[graph_name + '_num_paths'] = len(
            list(networkx.algorithms.simple_paths.all_simple_paths(g, test_node, component_node)))
        if self.features[graph_name + '_num_paths']:
            self.features[graph_name + '_shortest_path_length'] = networkx.algorithms.shortest_path_length(g, test_node, component_node)
        else:
            self.features[graph_name + '_shortest_path_length'] = -1
        self.features[graph_name + '_target_in_degree'] = g.in_degree(component_node)
        self.features[graph_name + '_source_degree_centrality'] = networkx.algorithms.centrality.degree_centrality(g)[
            test_node]
        self.features[graph_name + '_target_degree_centrality'] = networkx.algorithms.centrality.degree_centrality(g)[
            component_node]
        self.features[graph_name + '_in_source_degree_centrality'] = \
        networkx.algorithms.centrality.in_degree_centrality(g)[test_node]
        self.features[graph_name + '_in_target_degree_centrality'] = \
        networkx.algorithms.centrality.in_degree_centrality(g)[component_node]
        self.features[graph_name + '_out_source_degree_centrality'] = \
        networkx.algorithms.centrality.out_degree_centrality(g)[test_node]
        self.features[graph_name + '_out_target_degree_centrality'] = \
        networkx.algorithms.centrality.out_degree_centrality(g)[component_node]

    def call_graph(self):
        self._graph(networkx.read_gexf(os.path.join(self.dir_id.call_graphs, self.test + ".gexf")), "call_graph")

    def execution_graph(self):
        self._graph(networkx.read_gexf(os.path.join(self.dir_id.execution_graphs, self.test + ".gexf")), "execution_graph")

    def semantic_name(self):
        REMOVED = '- '
        ADDED = '+ '
        UNCHANGED = '  '
        NOT_IN_INPUT = '? '
        distance_metrics = [textdistance.hamming, textdistance.mlipns, textdistance.levenshtein,
                   textdistance.damerau_levenshtein, textdistance.jaro_winkler, textdistance.jaro,
                   textdistance.strcmp95, textdistance.needleman_wunsch, textdistance.gotoh,
                   textdistance.smith_waterman]
        distance_functions = ['distance', 'similarity', 'normalized_distance', 'normalized_similarity']

        def count_type(diff, diff_type):
            return len(list(filter(lambda d: d.startswith(diff_type), diff)))

        for feature_name, test in [('full_name_', self.test), ('partial_name_', self.test.replace('test', ''))]:
            diff = list(difflib.ndiff(test, self.function))
            seq_match = difflib.SequenceMatcher(None, test, self.function)
            match = seq_match.find_longest_match(0, len(test), 0, len(self.function))
            self.features[feature_name + "_diff_removed"] = count_type(diff, REMOVED)
            self.features[feature_name + "_diff_added"] = count_type(diff, ADDED)
            self.features[feature_name + "_diff_unchanged"] = count_type(diff, UNCHANGED)
            self.features[feature_name + "_longest_substring"] = int(match.size)
            self.features[feature_name + "_longest_substring_ratio"] = float(seq_match.ratio())
            for metric in distance_metrics:
                for function in distance_functions:
                    self.features[feature_name + "{0}_{1}".format(metric.__class__.__name__, function)] = \
                        float(getattr(metric, function)(test, self.function))

    def javadoc(self):
        re_sent_ends_naive = re.compile(r'[.\n]')
        re_stripper_alpha = re.compile('[^a-zA-Z]+')
        re_stripper_naive = re.compile('[^a-zA-Z\.\n]')

        splitter_naive = lambda x: re_sent_ends_naive.split(re_stripper_naive.sub(' ', x))

        sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')

        def get_tuples_nosentences(txt, n):
            """Get tuples that ignores all punctuation (including sentences)."""
            if not txt: return None
            ng = ngrams(re_stripper_alpha.sub(' ', txt).split(), n)
            return list(ng)

        def get_tuples_manual_sentences(txt, n):
            """Naive get tuples that uses periods or newlines to denote sentences."""
            if not txt: return None
            sentences = (x.split() for x in splitter_naive(txt) if x)
            ng = (ngrams(x, n) for x in sentences if len(x) >= n)
            return list(chain(*ng))

        def get_tuples_nltk_punkt_sentences(txt, n):
            """Get tuples that doesn't use textblob."""
            if not txt: return None
            sentences = (re_stripper_alpha.split(x) for x in sent_detector.tokenize(txt) if x)
            # Need to filter X because of empty 'words' from punctuation split
            ng = (ngrams(list(filter(None, x)), n) for x in sentences if len(x) >= n)
            return list(chain(*ng))

        def get_tuples_textblob_sentences(txt, n):
            """New get_tuples that does use textblob."""
            from textblob import TextBlob
            if not txt: return None
            tb = TextBlob(txt)
            ng = (ngrams(x.words, n) for x in tb.sentences if len(x.words) > n)
            return [item for sublist in ng for item in sublist]

        def jaccard_distance(a, b):
            """Calculate the jaccard distance between sets A and B"""
            a = set(a)
            b = set(b)
            if len(a | b):
                return 1.0 * len(a & b) / len(a | b)
            return 0

        def cosine_similarity_ngrams(a, b):
            vec1 = Counter(a)
            vec2 = Counter(b)

            intersection = set(vec1.keys()) & set(vec2.keys())
            numerator = sum([vec1[x] * vec2[x] for x in intersection])

            sum1 = sum([vec1[x] ** 2 for x in vec1.keys()])
            sum2 = sum([vec2[x] ** 2 for x in vec2.keys()])
            denominator = math.sqrt(sum1) * math.sqrt(sum2)

            if not denominator:
                return 0.0
            return float(numerator) / denominator

        stemmer = nltk.stem.porter.PorterStemmer()

        def stem_tokens(tokens):
            return [stemmer.stem(item) for item in tokens]

        def normalize(text):
            return stem_tokens(list(filter(lambda x: x not in stopwords.words('english'), nltk.word_tokenize(list(filter(lambda x: x not in string.punctuation, MLStripper.strip_tags(text).lower()))))))
        #
        # def ngrams(text, n):
        #     return Counter(zip(*[normalize(text)[i:] for i in range(n)]))

        def find_doc(func_name):
            with open(self.dir_id.javadoc) as f:
                data = json.loads(f.read())
            for classes_list in data:
                for class_dict in classes_list['classes']:
                    if class_dict['name'].lower() not in func_name:
                        continue
                    class_doc = class_dict['comment_text']
                    for method in class_dict['methods'] + class_dict['constructors']:
                        if method['name'].lower() in func_name:
                            method_doc = method['comment_text']
                            params_doc = ".".join(list(map(lambda p: p['comment_text'], method['parameters'])))
                            return class_doc, method_doc, params_doc

        def get_doc(func_name):
            lst = zip(["class_doc", "method_doc", "params_doc"], find_doc(func_name))
            for combination in chain(*(combinations(lst, i) for i in range(1, len(lst) + 1))):
                names, docs = zip(*combination)
                yield "_".join(names), ".".join(docs)

        for test_doc_name, test_doc in get_doc(self.test):
            if not test_doc:
                continue
            for func_doc_name, func_doc in get_doc(self.function):
                if not func_doc:
                    continue
                from sklearn.feature_extraction.text import TfidfVectorizer
                vectorizer = TfidfVectorizer(tokenizer=normalize, stop_words='english')
                # tfidf = vectorizer.fit_transform([test_doc, func_doc])
                # self.features["cosine_sim_{0}_{1}".format(test_doc_name, func_doc_name)] = ((tfidf * tfidf.T).A)[0,1]
                for n in range(2, 6):
                    from nltk.util import ngrams  # This is the ngram magic.
                    for getter in [get_tuples_manual_sentences, get_tuples_nltk_punkt_sentences, get_tuples_nosentences, get_tuples_textblob_sentences]:
                        test_ngrams = getter(test_doc, n)
                        function_ngrams = getter(func_doc, n)
                        self.features["ngrams_{0}_{1}_{2}_{3}_total".format(test_doc_name, func_doc_name, getter.__name__, n)] = len(test_ngrams + function_ngrams)
                        self.features["ngrams_{0}_{1}_{2}_{3}_common".format(test_doc_name, func_doc_name, getter.__name__, n)] = len(set(test_ngrams + function_ngrams))
                        self.features["ngrams_{0}_{1}_{2}_{3}_jaccard_distance".format(test_doc_name, func_doc_name, getter.__name__, n)] = jaccard_distance(test_ngrams, function_ngrams)
                        self.features["ngrams_{0}_{1}_{2}_{3}_cosine_similarity".format(test_doc_name, func_doc_name, getter.__name__, n)] = cosine_similarity_ngrams(test_ngrams, function_ngrams)

    def commits_data(self):
        with open(self.dir_id.files_functions) as f:
            files_functions = json.loads(f.read())
        with open(self.dir_id.files_commits) as f:
            files_commits = json.loads(f.read())
        test_commits = files_commits[files_functions[self.test + "()"]]
        function_commits = files_commits[files_functions[self.function]]
        self.features["common_commits"] = len(list(filter(lambda x: x[0] == x[1], zip(test_commits, function_commits))))
        REMOVED = '- '
        ADDED = '+ '
        UNCHANGED = '  '
        NOT_IN_INPUT = '? '

        def count_type(diff, diff_type):
            return len(list(filter(lambda d: d.startswith(diff_type), diff)))

        test_str = "".join(list(map(str, test_commits)))
        function_str = "".join(list(map(str, function_commits)))
        diff = list(difflib.ndiff(test_str, function_str))
        seq_match = difflib.SequenceMatcher(None, test_str, function_str)
        match = seq_match.find_longest_match(0, len(test_commits), 0, len(function_commits))
        self.features["commits_removed"] = count_type(diff, REMOVED)
        self.features["commits_added"] = count_type(diff, ADDED)
        self.features["commits_unchanged"] = count_type(diff, UNCHANGED)
        self.features["commits_substring"] = match.size
        self.features["commits_ratio"] = seq_match.ratio()


if __name__ == "__main__":
    # FeatureExtraction(DirId(DirStructure(r"C:\amirelm\component_importnace\data\d4j_lang12"), sys.argv[1])).extract()
    FeatureExtraction(DirId(DirStructure(r"C:\amirelm\component_importnace\data\d4j_lang12"), sys.argv[1])).get_training_set(DirStructure(r"C:\amirelm\component_importnace\data\d4j_lang12"))