#9 lines - Opening files

# indent your Python code to put into an email
import glob
# glob supports Unix style pathname extensions
python_files = glob.glob('*.py')
for fn in sorted(python_files):
    print '    ------', fn
    for line in open(fn):
        print '    ' + line.rstrip()
    print
