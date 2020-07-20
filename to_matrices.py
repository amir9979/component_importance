import os
import json
from sfl.Diagnoser.diagnoserUtils import readPlanningFile, write_planning_file

# obs = ["0aa57f04ede369a4f813bbb86d3eac1ed20b084c", "0cc451d5e5cb565eb7311308466f487bc534ebaf",
#        "19f33e4e0d824e732d07f06a08567c27b3c808f3", "1c606c3d96838e595a0664cbafdd60caae34aa0e",
#        "229151ec41339450e4d4f857bf92ed080d3e2430", "3905071819a14403d1cdb9437d2e005adf18fc70",
#        "3b46d611b2d595131ce0bce9bdb3209c55391be7", "3cea4b2af3f9caf6aa72fa56d647c513d320e073",
#        "3f900a7395e31eaa72e0fa2fb43c090e5a8fa4ed", "48bf241d4149919e0928e39616bee2e3783e2987",
#        "5209cefa81c9c48a34e5472fdcf2a308a4da2589", "575be16474e8e8246d4bbde6f243fdf38c34ad5b",
#        "68217617c54467c7c6098168e714a2fb6a48847d", "8da5fb28a764eee26c76a5018c293f224017887b",
#        "ac2a39e92a71d5f9eb3ca7c6cc789b6341c582a4", "ac58807ede6d9a0625b489cdca6fd37bad9cacfe",
#        "b2f1757bf9ec1632a940b9a2e65a1a022ba54af8", "b5906d3f325ca3a1147d5fa68912975e2e6c347e",
#        "b6f7a8a8be57c9525c59e9f21e958e76cee0dbaf", "cbf8e4eb017a99af9a8f24eb8429e8a12b62af8b",
#        "cf28c89dcf72d27573c478eb91e3b470de060edd", "cfff06bead88e2c1bb164285f89503a919e0e27f",
#        "e28c95ac2ce95852add84bdf3d2d9c00ac98f5de", "ec0c4e5508dbd8af83253f7c50f8b728a1003388"]


class ClonesPaths(object):
    def __init__(self, base_path):
        self.base_path = base_path
        self.commits = os.listdir(self.base_path)
        self.buggy_components = json.loads(open(os.path.join(self.base_path, r"buggy_commits.json")).read())
        self.traces_path = os.path.join(self.base_path, r"traces")
        self.traces_json_path = os.path.join(self.base_path, r"traces_json")
        self.call_graphs = os.path.join(self.base_path, r"call_graphs")
        self.execution_graphs = os.path.join(self.base_path, r"execution_graphs")
        self.obs_path = os.path.join(self.base_path, r"observations")
        self.matrices_path = os.path.join(self.base_path, r"matrices")
        self.tests_to_watch = os.path.join(self.base_path, r"tests_to_watch.json")

    def generate_test_to_watch(self):
        tests_to_watch = dict()
        for commit in self.commits:
            tests_of_commits = []
            diagnosis_file = os.path.join(self.matrices_path, commit + ".matrix")
            bugs = map(lambda b: b.split('@')[1].lower().replace(',', ';'), self.buggy_components[commit])
            with open(os.path.join(self.obs_path, commit + ".json")) as f:
                observations = json.loads(f.read())
            clean_observations = dict(
                map(lambda o: (o["_tast_name"].lower(), 0 if o["_outcome"] == "pass" else 1), observations))
            traces_dir = os.path.join(self.traces_json_path, commit)
            tests_details = []
            for test in clean_observations:
                if not os.path.exists(os.path.join(traces_dir, test + ".json")):
                    continue
                with open(os.path.join(traces_dir, test + ".json")) as f:
                    trace = json.loads(f.read())
                nice_trace = map(
                    lambda t: t.lower().replace("java.lang.", "").replace("java.io.", "").replace("java.util.", ""),
                    trace)
                if any(map(lambda x: x in nice_trace, bugs)):
                    tests_of_commits.append((test, clean_observations[test], filter(lambda x: x in nice_trace, bugs)))
                tests_details.append((test, nice_trace, clean_observations[test]))
            tests_to_watch[commit] = tests_of_commits
            write_planning_file(diagnosis_file, bugs, tests_details)

        with open(self.tests_to_watch, "wb") as f:
            json.dump(tests_to_watch, f)


for path in [r"C:\amirelm\component_importnace\data\d4j_lang", r"C:\amirelm\component_importnace\data\rotem_lang"]:
    obj = ClonesPaths(path)
    obj.generate_test_to_watch()