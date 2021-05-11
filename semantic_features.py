import difflib
import similarity
import textdistance


def count_type(diff, diff_type):
	return len(list(filter(lambda d: d.startswith(diff_type), diff)))

def count_diff_changes(diff):
	REMOVED = '- '
	ADDED = '+ '
	UNCHANGED = '  '
	NOT_IN_INPUT = '? '
	return count_type(diff, REMOVED), count_type(diff, ADDED), count_type(diff, UNCHANGED)

def distance(test_name, component_name):
	metrics = [textdistance.hamming, textdistance.mlipns, textdistance.levenshtein, textdistance.damerau_levenshtein, textdistance.jaro_winkler, textdistance.jaro, textdistance.strcmp95, textdistance.needleman_wunsch, textdistance.gotoh, textdistance.smith_waterman]
	functions = ['distance', 'similarity', 'normalized_distance', 'normalized_similarity']
	values = []
	for metric in metrics:
		for function in functions:
			values.append(getattr(metric, function)(test_name, component_name))
	return values

def longets_substring(test_name, component_name):
	seq_match = difflib.SequenceMatcher(None, test_name, component_name)
	match = seq_match.find_longest_match(0, len(test_name), 0, len(component_name))
	return match.size, seq_match.ratio()

def semantic_names(test_name, component_name):
	results = []
	for test in [test_name, test_name.replace('test', '')]:
		results.extend(count_diff_changes(difflib.ndiff(test, component_name)))
		results.extend(longets_substring(test_name, component_name))
		results.extend(distance(test_name, component_name))
	return results
	
test_name, component_name = "testStandardInterval".lower(), "StandardInterval".lower()
sn = semantic_names(test_name, component_name)