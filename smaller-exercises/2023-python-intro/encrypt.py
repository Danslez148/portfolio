# recursive program to encrypt a message
# Daniel Schlesinger
# 25 April

string = input('Enter a message:\n')

def encrypt(s, k):  # initialises k as an index variable used to move through the string s
    if k == len(s):   # stopping case
        return ''
    else:
        c = s[k]  # stores current char
        if 97 <= ord(c) <= 122: # if the char is from a to y
            if c == 'z':    # if the char is z, goes to a
                new = 'a'
            else:
                new = chr(ord(c)+1) # moves all lower cases letter one backwards in the alphabet
            return new + encrypt(s, k+1) # adds the new character and moves on in the input string to carry on encrypting
        else:
            return c + encrypt(s, k+1) # if the character isnt a lower case letter, just returns the same characters

print('Encrypted message:') #prints output
print(encrypt(string, 0))