'''
Author: Dan Kaptijn
Date: 19/11/2020
PyVersion: 3.7.6

Aim: Create a system which calculates the winner in an election between 2 condidates after a certain amount of time
The ruler will be called the Archon
'''


''' IMPORT MODULES '''
# import sys


''' FUNCTIONS '''
def reset_vote():
    voted = False
    a = 50
    b = 50

    return a,b,voted

def update_count(vote, a, b):
    voted = True
    if vote == 1:
        a += 1
    if vote == 2:
        b += 1

    return a,b,voted


''' CODE START '''

Candidate_1 = 'Pericles'
Candidate_2 = 'Cimon'

support_1, support_2, voted = reset_vote()

print('Welcome to this simulation of elections between the political rivals of Pericles and Cimon\n')
print('You can cast a vote to affect the outcome of this election')
vote = int(input('Enter 1 to vote for Pericles, or 2 to vote for Cimon: '))
print(vote)
if vote == 1 or vote == 2:
    support_1, support_2, voted = update_count(vote, support_1, support_2)
if voted == False:
    vote = int(input('You must vote in this simulation\nEnter 1 to vote for Pericles, or 2 to vote for Cimon: '))
    support_1, support_2, voted = update_count(vote, support_1, support_2)

print('Percentage of votes for Pericles = ' + str( round( (support_1/(support_1+support_2))*100 ,2)) + '%')
print('Percentage of votes for Cimon = ' + str( round( (support_2/(support_1+support_2))*100 ,2)) + '%')
