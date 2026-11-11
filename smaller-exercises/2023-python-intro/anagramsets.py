# program to find anagram sets of given length
# Daniel Schlesinger
# 12 May 2023

f = open('EnglishWords.txt', 'r')
print('***** Anagram Set Search *****')
length = int(input('Enter word length:\n'))
print('Searching...')
newfile = input('Enter file name:\n')
print('Writing results...')
allanagrams = []

def dictionarycreate(s):
    dic = {}
    s = s.lower()
    for c in s:
        if c in dic:
            dic[c] += 1
        else:
            dic[c] = 1
    return dict(sorted(dic.items()))

while True:
    temp = f.readline()
    if temp.strip() == 'START':
        break
allwords = f.readlines()
f.close()

for word in allwords:
    word = word.strip()
    valid = True
    for l in allanagrams:
        if word in l:
            valid = False
    if len(word) == length and valid == True:
        anagrams = []
        refdic = dictionarycreate(word)
        for s in allwords:
            s = s.strip()
            if refdic == dictionarycreate(s):
                anagrams.append(s)
        if len(anagrams) > 1:
            allanagrams.append(sorted(anagrams))

newf = open(newfile, 'w')
for l in allanagrams:
    newf.write(str(l) + '\n')
newf.close()