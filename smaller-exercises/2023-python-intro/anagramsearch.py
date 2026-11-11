# program to find english anagrams of an input
# Daniel Schlesinger
# 12 May 2023

import io

print('***** Anagram Finder *****')

try:
    fwords = open('EnglishWords.txt', 'r')
    wordin = input('Enter a word: \n')
    anagrams = []
    
    def dictionarycreate(s):
        dic = {}
        s = s.lower()
        for c in s:
            if c in dic:
                dic[c] += 1
            else:
                dic[c] = 1
        return dict(sorted(dic.items()))
    
    refdic = dictionarycreate(wordin)
    
    while True:
        temp = fwords.readline()
        if temp.strip() == 'START':
            break
        
    allwords = fwords.readlines()
    fwords.close()
    
    for s in allwords:
        s = s.strip()
        if s != wordin.lower():
            if dictionarycreate(s) == refdic:
                anagrams.append(s)
            
    if len(anagrams) == 0:
        print("Sorry, anagrams of '" + wordin + "' could not be found.")
    else:
        print(sorted(anagrams))      
except FileNotFoundError:
    print("Sorry, could not find file 'EnglishWords.txt'.")