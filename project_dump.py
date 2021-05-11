from run_process import main_cmds
import csv
import json
from tempfile import mktemp
import os


def create_csv_for_project(project, num_processes=15):
    dirs = list(map(lambda x: project.lower() + str(x), range(20)))
    dir_name = None
    listdir = os.listdir(r'd:\amirelm\component_importnace\data')
    for dir in dirs:
        if dir in listdir:
            dir_name = os.path.join(r'd:\amirelm\component_importnace\data', dir)
            # os.mkdir(dir_name)
            print(dir_name)
            break
    assert dir_name
    cmds = list(map(lambda x: ["python.exe", "d4j.py", dir_name, project, str(x)], range(200)))
    main_cmds(num_processes, cmds)


if __name__ == "__main__":
    create_csv_for_project('Lang')
