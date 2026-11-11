# program to assist with debugging Python programs
# Daniel Schlesinger
# 12 May 2023

print('***** Program Trace Utility *****')
modname = input('Enter the name of the program file: ')

try:
    fmodule = open(modname, 'r')
except IOError:
    print("Sorry, could not find file '" + modname + "'.")
    exit()

mlines = fmodule.readlines()
fmodule.close()

debuglineindexes = []
moddedlines = []

if '"""DEBUG"""\n' in mlines:
    for i, line in enumerate(mlines):
        if line.find('"""DEBUG"""') != -1:
            debuglineindexes.append(i)
    debuglineindexes.reverse()
    for i, line in enumerate(mlines):
        if i not in debuglineindexes:
            moddedlines.append(line)

else:
    moddedlines.append('"""DEBUG"""\n')    
    for i, line in enumerate(mlines):
        moddedlines.append(line)
        if line[:4] == 'def ':
            functionname = line[4:line.find('(')]
            moddedlines.append('    """DEBUG""";print(\'' + functionname + '\')\n')

fmodule = open(modname, 'w')
fmodule.writelines(moddedlines)
fmodule.close

if len(debuglineindexes) != 0:
    print('Program contains trace statements')
    print('Removing...Done')
else:
    print('Inserting...Done')