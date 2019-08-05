import os


class FixLangClone(object):
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

    def clear(self):
        for builder_test in map(lambda t: os.path.join(self.clone_dir, t), FixLangClone.ToStringBuilderTest):
            if os.path.exists(builder_test):
                self.get_test_annotation(builder_test, "testReflectionHierarchyArrayList()")

        for test in map(lambda t: os.path.join(self.clone_dir, t), FixLangClone.FastDateFormatTest):
            if os.path.exists(test):
                self.get_test_annotation(test, "testFormat()")

        type_test = os.path.join(self.clone_dir, FixLangClone.TypeUtilsTest)
        type_test2 = os.path.join(self.clone_dir, FixLangClone.TypeUtilsTest2)
        if os.path.exists(type_test):
            self.search_line(type_test, "Integer max = TypeUtilsTest.stub();")
        elif os.path.exists(type_test2):
                self.search_line(type_test2, "Integer max = TypeUtilsTest.stub();")

        # fast_date_test = os.path.join(self.clone_dir, FixLangClone.FastDateParserTest)
        # fast_date_test2 = os.path.join(self.clone_dir, FixLangClone.FastDateParserTest2)
        # if os.path.exists(fast_date_test):
        #     self.get_test_annotation(fast_date_test, "testParseZone()")
        # elif os.path.exists(fast_date_test2):
        #     self.get_test_annotation(fast_date_test2, "testParseZone()")

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
        test_line = filter(lambda x: test_name in x[1], enumerate(lines))
        if test_line:
            test_line = test_line[0][0]
        else:
            return
        if annotation in lines[test_line - 1]:
            self.comment_line(test_file, test_line - 1)
        self.rename_test(test_file, test_name)

    def rename_test(self, test_file, test_name):
        with open(test_file) as f:
            lines = f.readlines()
        test_line = filter(lambda x: test_name in x[1], enumerate(lines))
        if len(test_line) == 1:
            lines[test_line[0][0]] = lines[test_line[0][0]].replace("test", "non_test")
            with open(test_file, "w") as f:
                f.writelines(lines)

    def search_line(self, test_file, line):
        with open(test_file) as f:
            lines = f.readlines()
        test_line = filter(lambda x: line in x[1], enumerate(lines))
        if len(test_line) == 1:
            return self.comment_line(test_file, test_line[0][0])


if __name__ == "__main__":
    FixLangClone(r"C:\amirelm\component_importnace\data\d4j_lang3\clones\2c454a4ce3fe771098746879b166ede2284b94f4").clear()
    # path = r"C:\amirelm\component_importnace\data\d4j_lang3\clones"
    # map(lambda x: FixLangClone(os.path.join(path,x)).clear(), os.listdir(path))