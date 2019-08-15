from project_fixer import project_fixer
from d4j import D4J
import os


class D4JLang(D4J):
    LANG_REPO = r"C:\temp\defects4j-lang"
    LANG_D4J_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), r"projects\lang"))
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

    def __init__(self, id, buggy, fixed, bug_key, bug_url, json_data, dir_id):
        super(D4JLang, self).__init__(id, buggy, fixed, bug_key, bug_url, json_data, dir_id)

    def get_repo(self):
        return D4JLang.LANG_REPO

    def get_patches_dir(self):
        return os.path.join(D4JLang.LANG_D4J_DIR, "patches")

    def fix(self):
        fixer = project_fixer(self.get_dir_id().clones)
        fixer.clear_test_in_files("testReflectionHierarchyArrayList()", D4JLang.ToStringBuilderTest)
        fixer.clear_test_in_files("testFormat()", D4JLang.FastDateFormatTest)
        fixer.comment_line_in_files("Integer max = TypeUtilsTest.stub();", [D4JLang.TypeUtilsTest, D4JLang.TypeUtilsTest2])

