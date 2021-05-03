import os
import json
import networkx
import csv
import itertools


call_graphs = r"C:\amirelm\component_importnace\data\d4j_lang\call_graphs"
execution_graphs = r"C:\amirelm\component_importnace\data\d4j_lang\execution_graphs"

def get_graph_features(g, source, target, name_initial):
	features = dict()
	features[name_initial + '_shortest_path_length'] = networkx.algorithms.shortest_path_length(g, source, target)
	features[name_initial + '_num_paths'] = len(list(networkx.algorithms.simple_paths.all_simple_paths(g, source, target)))
	features[name_initial + '_target_in_degree'] = g.in_degree(target)
	features[name_initial + '_source_degree_centrality'] = networkx.algorithms.centrality.degree_centrality(g)[source]
	features[name_initial + '_target_degree_centrality'] = networkx.algorithms.centrality.degree_centrality(g)[target]
	features[name_initial + '_in_source_degree_centrality'] = networkx.algorithms.centrality.in_degree_centrality(g)[source]
	features[name_initial + '_in_target_degree_centrality'] = networkx.algorithms.centrality.in_degree_centrality(g)[target]
	features[name_initial + '_out_source_degree_centrality'] = networkx.algorithms.centrality.out_degree_centrality(g)[source]
	features[name_initial + '_out_target_degree_centrality'] = networkx.algorithms.centrality.out_degree_centrality(g)[target]
	return features


instances = []
with open(r"C:\amirelm\component_importnace\data\d4j_lang\tests_to_watch.json") as f:
	tests_to_watch = json.loads(f.read())
	
for commit in tests_to_watch:
	for commit_test in tests_to_watch[commit]:
		for test, observation, component in itertools.product([commit_test[0]],[commit_test[1]],commit_test[2]):
			features = {"observation" : observation}
			for g_type in [call_graphs, execution_graphs]:
				graph = networkx.read_gexf(os.path.join(g_type, commit, test+".gexf"))
				test_node = filter(lambda node: test in node.lower(), graph.node)[0]
				component_node = filter(lambda node: component in node.lower().replace("java.lang.", "").replace("java.io.", "").replace("java.util.", ""), graph.node)[0]
				features.update(get_graph_features(graph, test_node, component_node, os.path.basename(g_type)))
			instances.append(features)
		

with open(r"C:\amirelm\component_importnace\data\d4j_lang\training_graph.json", "wb") as f:
	json.dump(instances, f)
	
keys = sorted(instances[0].keys())
lines = list(map(lambda i: list(map(lambda k: i[k], keys)), instances))
with open(r"C:\amirelm\component_importnace\data\d4j_lang\training_graph.csv", "wb") as f:
	csv.writer(f).writerows([keys] + lines)

