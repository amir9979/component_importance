import csv
lines = open(r"C:\temp\math.txt").readlines()
clones = list(map(lambda x: r"git clone C:\temp\commons-lang C:\amirelm\component_importnace\data\d4j_math\clones\{0}".format(x), lines))
checkouts = list(map(lambda x: r"git -C C:\amirelm\component_importnace\data\d4j_math\clones\{0} checkout {0}".format(x), lines))
new_lines = clones + checkouts
map(lambda x: x.split(), new_lines)
new_lines2 = list(map(lambda x: x.split(), new_lines))
csv.writer(open(r"c:\temp\d4j_math.csv", "w")).writerows(new_lines2)