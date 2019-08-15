import csv
import json
import git
import os
from mvnpy.Repo import Repo
from subprocess import Popen
from dir_structure import DirStructure, DirId
import networkx
from sfl_diagnoser.Diagnoser.diagnoserUtils import write_json_planning_file, read_json_planning_file
import javadiff.diff
from javadiff.SourceFile import SourceFile
from mvnpy.jcov_parser import JcovParser
import sys
from feature_extraction import FeatureExtraction


class D4J(object):
    D4J_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), r"projects"))
    D4J_JSON = os.path.realpath(os.path.join(os.path.dirname(__file__), r"defects4j-bugs.json"))

    def __init__(self, id, buggy, fixed, bug_key, bug_url, json_data, dir_id):
        self.id, self.buggy, self.fixed, self.bug_key, self.bug_url = id, buggy, fixed, bug_key, bug_url
        self.json_data = json_data
        self.failing_tests_by_json = map(lambda x: "{0}.{1}".format(x['className'], x['methodName']).strip().lower(), self.json_data['failingTests'])
        self.surefire_tests = []
        self.tests_to_trace = []
        self.traces = []
        self.optimized_traces = []
        self.bugs = []
        self.dir_id = dir_id

    def get_repo(self):
        return D4JLang.LANG_REPO

    def clone(self):
        Popen(['git', 'clone', self.get_repo(), self.dir_id.clones]).wait()
        Popen(['git', '-C', self.dir_id.clones, "checkout", self.fixed]).wait()

    def get_patches_dir(self):
        return os.path.join(D4JLang.LANG_D4J_DIR, "patches")

    def apply_patch(self):
        repo = git.Repo(self.dir_id.clones)
        test_patch = os.path.join(self.get_patches_dir(), self.id) + ".src.patch"
        if os.path.exists(test_patch):
            repo.git.apply(test_patch)

    def fix(self):
        pass

    def read_test_results(self):
        repo = Repo(self.dir_id.clones)
        self.surefire_tests = repo.observe_tests()

    def clean_execution(self):
        repo = Repo(self.dir_id.clones)
        build_report = repo.install()
        with open(self.dir_id.mvn_outputs, "w") as f:
            f.write(build_report)

    def trace(self):
        repo = Repo(self.dir_id.clones)
        DirStructure.mkdir(self.dir_id.traces)
        if self.traces:
            return
        if self.is_marked():
            traces = list(JcovParser(self.dir_id.traces).parse())
        else:
            traces = list(repo.run_under_jcov(self.dir_id.traces, False, instrument_only_methods=True))
        self.traces = dict(map(lambda t: (t.test_name, t), traces))

    def get_optimized_traces(self):
        self.trace()
        self.get_tests_to_trace()
        all_tests = filter(lambda x: x, map(self.traces.get, self.tests_to_trace))
        fail_tests = filter(lambda test: self.surefire_tests[test.test_name].outcome != 'pass', all_tests)
        fail_components = reduce(set.__or__, map(lambda test: set(test.get_trace()), fail_tests), set())
        self.optimized_traces = dict(map(lambda t: (t.test_name, t), filter(lambda test: fail_components & set(test.get_trace()), all_tests)))

    def get_tests_to_trace(self):
        self.read_test_results()
        if 'pass' in map(lambda test: self.surefire_tests[test].outcome, self.failing_tests_by_json):
            return False
        self.tests_to_trace = []
        for test in self.surefire_tests:
            add = False
            if self.surefire_tests[test].outcome != 'pass':
                add = test in self.failing_tests_by_json
            elif self.surefire_tests[test].outcome == 'pass':
                add = test not in self.failing_tests_by_json
            if add:
                self.tests_to_trace.append(test)
        return True

    def get_dir_id(self):
        return self.dir_id

    def get_buggy_functions(self):
        if self.is_marked() and os.path.exists(self.dir_id.bugs):
            with open(self.dir_id.bugs) as f:
                self.bugs = json.loads(f.read())
        else:
            self.bugs = map(lambda x: x.split("@")[1].lower().replace(',', ';'), javadiff.diff.get_modified_functions(self.dir_id.clones))
            with open(self.dir_id.bugs, "wb") as f:
                json.dump(self.bugs, f)
        if self.bugs:
            return True
        return False

    def clear(self):
        git.Repo(self.dir_id.clones).git.checkout('--', '.')

    def mark(self):
        with open(self.dir_id.mark, "w") as f:
            f.write("executed_succesfully")

    def is_marked(self):
        return os.path.exists(self.dir_id.mark)

    def dump(self):
        if self.is_marked():
            return
        self.clone()
        self.clear()
        self.apply_patch()
        if not self.get_buggy_functions():
            return
        self.fix()
        self.clean_execution()
        if self.get_tests_to_trace():
            self.trace()
            if self.get_tests_to_trace():
                self.mark()
                self.save_as_sfl_matrix()

    def save_as_sfl_matrix(self):
        if self.is_marked() or True:
            self.get_optimized_traces()
            self.get_buggy_functions()
            tests_details = []
            bugs = map(lambda b: b.replace(',', ';'), self.bugs)
            print bugs
            for test in self.optimized_traces.values():
                nice_trace = list(set(map(
                    lambda t: t.lower().replace("java.lang.", "").replace("java.io.", "").replace("java.util.", ""),
                    test.get_trace())))
                if test.test_name + "()" in nice_trace:
                    nice_trace.remove(test.test_name + "()")
                tests_details.append((test.test_name, nice_trace, 0 if self.surefire_tests[test.test_name].outcome == 'pass' else 1))
            write_json_planning_file(self.dir_id.matrices, tests_details, bugs)

    def get_files_packages(self):
        sources_path = r'src/main/java'
        packages = dict()
        repo = git.Repo(self.dir_id.clones)
        for file_name in filter(lambda f: sources_path in f, repo.git.ls_files().split('\n')):
            packages[os.path.normpath(file_name.split('.java')[0].split(sources_path)[1]).replace(os.sep, '.')[1:]] = file_name
        with open(self.dir_id.files_packages, "wb") as f:
            json.dump(packages, f)
        return packages

    def get_files_commits(self):
        sources_path = r'src/main/java'
        test_sources_path = r'src/test/java'
        commits = dict()
        repo = git.Repo(self.dir_id.clones)
        repo_commits = map(lambda x: x.hexsha[:7], list(repo.iter_commits()))
        for file_name in filter(lambda f: sources_path in f or test_sources_path in f, repo.git.ls_files().split('\n')):
            file_commits = map(lambda x: x[:7], repo.git.log('--pretty=format:%h', file_name).split('\n'))
            commits[file_name] = map(lambda c: 1 if c in file_commits else 0, repo_commits)
        with open(self.dir_id.files_commits, "wb") as f:
            json.dump(commits, f)
        return commits

    def get_files_functions(self):
        sources_path = r'src/main/java'
        test_sources_path = r'src/test/java'
        repo = git.Repo(self.dir_id.clones)
        files_functions = {}
        for file_name in filter(lambda f: sources_path in f or test_sources_path in f, repo.git.ls_files().split('\n')):
            with open(os.path.join(self.dir_id.clones, file_name)) as f:
                map(lambda m: files_functions.setdefault(m.id.split("@")[1].lower().replace(',', ';'), file_name), SourceFile(f.read(), file_name).methods.values())
        with open(self.dir_id.files_functions, "wb") as f:
            json.dump(files_functions, f)

    def generate_javadoc(self):
        repo = Repo(self.dir_id.clones)
        repo.javadoc_command(self.dir_id.javadoc)

    def execution_graph(self):
        DirStructure.mkdir(self.dir_id.execution_graphs)
        for trace in self.optimized_traces:
            g = networkx.DiGraph()
            g.add_edges_from(self.optimized_traces[trace].get_execution_edges())
            networkx.write_gexf(g, os.path.join(self.dir_id.execution_graphs, trace + ".gexf"))

    def call_graph(self):
        DirStructure.mkdir(self.dir_id.call_graphs)
        for trace in self.optimized_traces:
            g = networkx.DiGraph()
            g.add_edges_from(self.optimized_traces[trace].get_call_graph_edges())
            networkx.write_gexf(g, os.path.join(self.dir_id.call_graphs, trace + ".gexf"))

    @staticmethod
    def dump_all_projects(projects):
        map(lambda p: p.dump(), projects)

    def data_extraction(self):
        if not self.is_marked():
            return
        self.get_optimized_traces()
        self.call_graph()
        self.execution_graph()
        self.generate_javadoc()
        self.get_files_commits()
        self.get_files_packages()
        self.get_files_functions()
        self.labels()
        self.save_traces()

    def labels(self):
        self.get_tests_to_trace()
        self.get_buggy_functions()
        labels = {}
        bugs = map(lambda b: b.replace(',', ';'), self.bugs)
        for test in self.optimized_traces.values():
            nice_trace = list(set(map(
                lambda t: t.lower().replace("java.lang.", "").replace("java.io.", "").replace("java.util.", ""),
                test.get_trace())))
            for bug in filter(nice_trace.__contains__, bugs):
                labels.setdefault(test.test_name, dict())[bug] = self.surefire_tests[test.test_name].outcome == 'pass'
        with open(self.dir_id.labels, "wb") as f:
            json.dump(labels, f)

    def save_traces(self):
        self.get_optimized_traces()
        traces = dict()
        for test in self.optimized_traces.values():
            nice_trace = list(set(map(
                lambda t: t.lower().replace("java.lang.", "").replace("java.io.", "").replace("java.util.", ""),
                test.get_trace())))
            traces[test.test_name] = nice_trace
            if test.test_name + "()" in nice_trace:
                nice_trace.remove(test.test_name + "()")
        with open(self.dir_id.traces_json, "wb") as f:
            json.dump(traces, f)

    @staticmethod
    def read_commit_db(dir_path, project='Lang'):
        d4j = json.load(open(D4J.D4J_JSON))
        project_data = dict(map(lambda x: (str(x['bugId']), x), filter(lambda x: x['project'].lower() == project.lower(), d4j)))
        projects = []
        with open(os.path.join(D4J.D4J_DIR, project, "commit-db")) as f:
            for id, buggy, fixed, bug_key, bug_url in csv.reader(f):
                projects.append(D4J.project_class(project)(id, buggy, fixed, bug_key, bug_url, project_data[id], DirId(DirStructure(dir_path), id)))
        return projects

    def save_tests_results(self):
        self.get_optimized_traces()
        data = dict(map(lambda t: (t, self.surefire_tests[t].outcome == 'pass'), self.optimized_traces))
        with open(self.dir_id.tests_results, "wb") as f:
            json.dump(data, f)

    def do_all(self):
        self.dump()
        self.data_extraction()
        if self.is_marked():
            FeatureExtraction(self.dir_id).extract()

    @staticmethod
    def project_class(project='Lang'):
        from d4j_lang import D4JLang
        from d4j_math import D4JMath
        project_dict = {'Lang': D4JLang, 'Math': D4JMath}
        return project_dict.get(project)


if __name__ == "__main__":
    projects = D4J.read_commit_db(r"C:\amirelm\component_importnace\data\d4j_lang13", 'Lang')
    projects[int(sys.argv[1])].do_all()
    # projects[int(sys.argv[1])].labels()
    # projects[int(sys.argv[1])].save_traces()
    exit()
