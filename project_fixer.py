import os


class project_fixer(object):
    ToStringBuilderTest = [r"src/test/java/org/apache/commons/lang3/builder/ToStringBuilderTest.java",
                           r"src/test/org/apache/commons/lang3/builder/ToStringBuilderTest.java",
                           r"src/test/org/apache/commons/lang/builder/ToStringBuilderTest.java"]
    TypeUtilsTest = r"src/test/java/org/apache/commons/lang3/reflect/TypeUtilsTest.java"
    TypeUtilsTest2 = r"src/test/org/apache/commons/lang3/reflect/TypeUtilsTest.java"
    FastDateParserTest = r"src/test/java/org/apache/commons/lang3/time/FastDateParserTest.java"
    FastDateParserTest2 = r"src/test/org/apache/commons/lang3/time/FastDateParserTest.java"
    FastDateFormatTest = [r"src\test\java\org\apache\commons\lang3\time\FastDateFormatTest.java",
                          r"src\test\org\apache\commons\lang3\time\FastDateFormatTest.java",
                          r"src\test\org\apache\commons\lang\time\FastDateFormatTest.java"]

    def __init__(self, clone_dir):
        self.clone_dir = clone_dir

    def clear_test_in_files(self, test_name, files):
        for file_path in map(lambda t: os.path.join(self.clone_dir, t), files):
            if os.path.exists(file_path):
                self.get_test_annotation(file_path, test_name)

    def comment_line_in_files(self, line, files):
        for file_path in map(lambda t: os.path.join(self.clone_dir, t), files):
            if os.path.exists(file_path):
                self.search_line(file_path, line)

    def comment_line(self, test_file, line_number):
        with open(test_file) as f:
            lines = f.readlines()
        lines[line_number] = "//" + lines[line_number]
        with open(test_file, "w") as f:
            f.writelines(lines)

    def get_test_annotation(self, test_file, test_name):
        annotation = "@Test"
        with open(test_file) as f:
            lines = f.readlines()
        test_lines = map(lambda t: t[0], filter(lambda x: test_name in x[1], enumerate(lines)))
        if not test_lines:
            return
        for test_line in test_lines:
            if annotation in lines[test_line - 1]:
                self.comment_line(test_file, test_line - 1)
            self.rename_test(test_file, test_name)

    def rename_test(self, test_file, test_name):
        with open(test_file) as f:
            lines = f.readlines()
        test_lines = filter(lambda x: test_name in x[1], enumerate(lines))
        for test_line in test_lines:
            lines[test_line[0]] = lines[test_line[0]].replace("test", "non_test")
            with open(test_file, "w") as f:
                f.writelines(lines)

    def search_line(self, test_file, line):
        with open(test_file) as f:
            lines = f.readlines()
        test_line = filter(lambda x: line in x[1], enumerate(lines))
        if len(test_line) == 1:
            return self.comment_line(test_file, test_line[0][0])