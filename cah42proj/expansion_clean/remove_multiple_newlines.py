import re
sourceFileName = "1_clean.txt"

with open(sourceFileName, 'rt') as sourceFile:
	sourceFileContents = ''.join([l.rstrip() + '\n' for l in sourceFile])
	print(sourceFileContents)
	a = re.sub(r'(\n\s*)+\n+', '\n\n', sourceFileContents)
	print(a)
	with open("output.txt", "wt") as f:
		f.write(a)
