# recursive program to find the number of pairs in a string
# Daniel Schlesinger
# 25 April

string = input('Enter a message:\n')

def pairs(s, n):
    if n + 1 >= len(s):
        return 0    # stops checking before the end (stopping case)
    elif s[n] == s[n+1]:
        return pairs(s, n+2) + 1   # if there is a pair, adds 1 to the count and carries on recursion for the character 2 after the current one
    else:
        return pairs(s, n+1)   # if there isn't a pair, carries on recursion for the next character
    
print('Number of pairs: ' + str(pairs(string, 0))) # prints output