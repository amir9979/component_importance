import csv
import json
import git
import os
from mvnpy.Repo import Repo
from lang_fix import FixLangClone
from subprocess import Popen
from dir_structure import DirStructure, DirId
import networkx
from sfl_diagnoser.Diagnoser.diagnoserUtils import write_json_planning_file, read_json_planning_file
import javadiff.diff
from mvnpy.jcov_parser import JcovParser
import sys


class D4JLang(object):
    LANG_REPO = r"C:\temp\defects4j-lang"
    LANG_D4J_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), r"projects\lang"))
    D4J_JSON = os.path.realpath(os.path.join(os.path.dirname(__file__), r"defects4j-bugs.json"))

    def __init__(self, id, buggy, fixed, bug_key, bug_url, json_data, dir_id):
        self.id, self.buggy, self.fixed, self.bug_key, self.bug_url = id, buggy, fixed, bug_key, bug_url
        self.json_data = json_data
        self.failing_tests_by_json = map(lambda x: "{0}.{1}".format(x['className'], x['methodName']).strip().lower(), self.json_data['failingTests'])
        self.surefire_tests = []
        self.tests_to_trace = []
        self.traces = []
        self.bugs = []
        self.dir_id = dir_id

    def clone(self):
        Popen(['git', 'clone', D4JLang.LANG_REPO, self.dir_id.clones]).wait()
        Popen(['git', '-C', self.dir_id.clones, "checkout", self.fixed]).wait()

    def apply_patch(self):
        repo = git.Repo(self.dir_id.clones)
        test_patch = os.path.join(os.path.join(D4JLang.LANG_D4J_DIR, "patches"), self.id) + ".src.patch"
        if os.path.exists(test_patch):
            repo.git.apply(test_patch)

    def fix(self):
        FixLangClone(self.dir_id.clones).clear()

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
        if self.is_marked():
            self.traces = list(JcovParser(self.dir_id.traces).parse())
        else:
            self.traces = list(repo.run_under_jcov(self.dir_id.traces, False, instrument_only_methods=True))

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
            self.get_tests_to_trace()
            self.get_buggy_functions()
            self.trace()
            tests_details = []
            bugs = map(lambda b: b.replace(',', ';'), self.bugs)
            print bugs
            for test in self.traces:
                nice_trace = list(set(map(
                    lambda t: t.lower().replace("java.lang.", "").replace("java.io.", "").replace("java.util.", ""),
                    test.get_trace())))
                if test.test_name + "()" in nice_trace:
                    nice_trace.remove(test.test_name + "()")
                tests_details.append((test.test_name, nice_trace, 0 if self.surefire_tests[test.test_name].outcome == 'pass' else 1))
            write_json_planning_file(self.dir_id.matrices, tests_details, bugs)

    def get_files_packages(self, path_to_dump=None):
        sources_path = r'src/main/java'
        packages = dict()
        repo = git.Repo(self.dir_id.clones)
        for file_name in filter(lambda f: sources_path in f, repo.git.ls_files().split('\n')):
            packages[os.path.normpath(file_name.split('.java')[0].split(sources_path)[1]).replace(os.sep, '.')[1:]] = file_name
        if path_to_dump:
            dump(packages, path_to_dump)
        return packages

    def get_files_commits(self, path_to_dump=None):
        sources_path = r'src/main/java'
        commits = dict()
        repo = git.Repo(self.dir_id.clones)
        repo_commits = map(lambda x: x.hexsha[:7], list(repo.iter_commits()))
        for file_name in filter(lambda f: sources_path in f, repo.git.ls_files().split('\n')):
            file_commits = map(lambda x: x[:7], repo.git.log('--pretty=format:%h', file_name).split('\n'))
            commits[file_name] = map(lambda c: 1 if c in file_commits else 0, repo_commits)
        if path_to_dump:
            dump(commits, path_to_dump)
        return commits

    def generate_javadoc(self):
        repo = Repo(self.dir_id.clones)
        repo.javadoc_command(self.dir_id.javadoc)

    def execution_graph(self):
        DirStructure.mkdir(self.dir_id.execution_graphs)
        for trace in self.traces:
            g = networkx.DiGraph()
            g.add_edges_from(trace.get_execution_edges())
            networkx.write_gexf(g, os.path.join(self.dir_id.execution_graphs, trace.test_name + ".gexf"))

    def call_graph(self):
        DirStructure.mkdir(self.dir_id.call_graphs)
        for trace in self.traces:
            g = networkx.DiGraph()
            g.add_edges_from(trace.get_call_graph_edges())
            networkx.write_gexf(g, os.path.join(self.dir_id.call_graphs, trace.test_name + ".gexf"))

    @staticmethod
    def dump_all_projects(projects):
        map(lambda p: p.dump(), projects)

    @staticmethod
    def read_commit_db(dir_structure):
        d4j = json.load(open(D4JLang.D4J_JSON))
        lang = dict(map(lambda x: (str(x['bugId']), x), filter(lambda x: x['project'] == 'Lang', d4j)))
        projects = []
        with open(os.path.join(D4JLang.LANG_D4J_DIR, "commit-db")) as f:
            for id, buggy, fixed, bug_key, bug_url in csv.reader(f):
                projects.append(D4JLang(id, buggy, fixed, bug_key, bug_url, lang[id], DirId(dir_structure, id)))
        return projects


if __name__ == "__main__":
    projects = D4JLang.read_commit_db(DirStructure(r"C:\amirelm\component_importnace\data\d4j_lang8"))
    projects[int(sys.argv[1])].save_as_sfl_matrix()
