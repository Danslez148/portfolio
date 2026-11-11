# recursive program to find palindromic primes
# Daniel Schlesinger
# 25 April

import sys
sys.setrecursionlimit(30000)
import math

def palindrome(s, n, k): # initialise n and k and start and end variables used to keep track of index
    s = str(s)  # convert number to string
    if n >= k: # stopping case (once we've checked through the string enough)
        return True
    elif s[n] != s[k]: # if there is a point that shows s isn't a palindrome, stop recursion and return false
        return False
    else:
        return palindrome(s, n+1, k-1) # recursive step
        
def prime(n, k=3): # k is used as a base of the modulo function to check divisibility of n
    if n < 2:
        return False # base case
    elif n == 2:
        return True # base case
    elif n%2 == 0:  # checks all the odds numbers since k starts at 3
        return False
    elif k > math.sqrt(n): # stopping case, if it gets through all of the other integers it means it is prime
        return True
    elif n % k == 0:  # if there is a divisor return false
        return False
    else:
        return prime(n, k+2) # recursive step skips a number since we checked all the evens

def paliprime(N, M):
    if N <= M: # makes sure we stay inside bounds
        if palindrome(N, 0, len(str(N))-1) and prime(N): # if its a prime palindrome, we print it
            print(N)
        paliprime(N+1, M) # recursive step

N = int(input('Enter the starting point N:\n'))
M = int(input('Enter the ending point M:\n'))

print('The palindromic primes are:')
paliprime(N, M) # output