from project_fixer import project_fixer
from d4j import D4JReproducer
import os
import sys


class D4JMath(D4JReproducer):
    REPO = r"C:\temp\defects4j-math"
    D4J_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), r"projects\math"))

    def __init__(self, id, fixed, failing_tests, dir_id):
        super(D4JMath, self).__init__(id, fixed, failing_tests, dir_id)

    def get_repo(self):
        return D4JMath.REPO

    def get_patches_dir(self):
        return os.path.join(D4JMath.D4J_DIR, "patches")

    def fix(self):
        fixer = project_fixer(self.get_dir_id().clones)
        fixer.clear_test_in_files("testIssue464()", [r"src\test\java\org\apache\commons\math3\analysis\integration\IterativeLegendreGaussIntegratorTest.java",
                                                     r"src\test\java\org\apache\commons\math3\analysis\integration\LegendreGaussIntegratorTest.java"])

        # ignore high runtime tests
        high_runtime = [r"src\test\java\org\apache\commons\math3\analysis\interpolation\MicrosphereInterpolatorTest.java",
                        r"src\test\java\org\apache\commons\math3\dfp\BracketingNthOrderBrentSolverDFPTest.java",
                        r"src\test\java\org\apache\commons\math3\distribution\AbstractRealDistributionTest.java",
                        r"src\test\java\org\apache\commons\math3\distribution\KolmogorovSmirnovDistributionTest.java",
                        r"src\test\java\org\apache\commons\math3\distribution\LogNormalDistributionTest.java",
                        r"src\test\java\org\apache\commons\math3\geometry\euclidean\threed\RotationTest.java",
                        r"src\test\java\org\apache\commons\math3\linear\HessenbergTransformerTest.java",
                        r"src\test\java\org\apache\commons\math3\linear\SchurTransformerTest.java",
                        # r"src\test\java\org\apache\commons\math3\linear\UnmodifiableOpenMapRealVectorTest.java",
                        r"src\test\java\org\apache\commons\math3\ode\nonstiff\AdamsBashforthIntegratorTest.java",
                        r"src\test\java\org\apache\commons\math3\ode\nonstiff\ClassicalRungeKuttaIntegratorTest.java",
                        r"src\test\java\org\apache\commons\math3\ode\nonstiff\GillIntegratorTest.java",
                        r"src\test\java\org\apache\commons\math3\ode\nonstiff\GraggBulirschStoerIntegratorTest.java",
                        r"src\test\java\org\apache\commons\math3\ode\nonstiff\MidpointIntegratorTest.java",
                        r"src\test\java\org\apache\commons\math3\ode\nonstiff\ThreeEighthesIntegratorTest.java",
                        r"src\test\java\org\apache\commons\math3\optimization\direct\BOBYQAOptimizerTest.java",
                        r"src\test\java\org\apache\commons\math3\distribution\PoissonDistributionTest.java",
                        r"src\test\java\org\apache\commons\math3\linear\BlockFieldMatrixTest.java",
                        r"src\test\java\org\apache\commons\math3\analysis\differentiation\DerivativeStructureTest.java",
                        r"src\test\java\org\apache\commons\math3\analysis\differentiation\GradientFunctionTest.java",
                        r"src\test\java\org\apache\commons\math3\distribution\FDistributionTest.java",
                        r"src\test\java\org\apache\commons\math3\distribution\MultivariateNormalDistributionTest.java",
                        r"src\test\java\org\apache\commons\math3\distribution\TriangularDistributionTest.java",
                        r"src\test\java\org\apache\commons\math3\linear\BlockRealMatrixTest.java",
                        r"src\test\java\org\apache\commons\math3\linear\SymmLQTest.java",
                        r"src\test\java\org\apache\commons\math3\linear\UnmodifiableOpenMapRealVectorTest.java",
                        r"src\test\java\org\apache\commons\math3\optimization\fitting\PolynomialFitterTest.java",
                        r"src\test\java\org\apache\commons\math3\optimization\general\GaussNewtonOptimizerTest.java",
                        r"src\test\java\org\apache\commons\math3\optimization\general\MinpackTest.java",
                        r"src\test\java\org\apache\commons\math3\linear\UnmodifiableOpenMapRealVectorTest.java",
                        r"src\test\java\org\apache\commons\math3\linear\TriangularDistributionTest.java",
                        r"src\test\java\org\apache\commons\math3\linear\FDistributionTest.java"]

        fixer.clear_test_in_files("void test", high_runtime)


if __name__ == "__main__":
    projects = D4JReproducer.read_commit_db(r"C:\amirelm\component_importnace\data\_math6", 'Math')
    projects[18].do_all()