# -*- coding: utf-8 -*-
"""
Created on Thu Oct 10 19:44:19 2019

@author: Matthew
"""

from tqdm import tqdm
from Hangman import HangmanAPI
                        
train = HangmanAPI()
test = HangmanAPI()

for i in tqdm(range(10)):
    train.start_game(verbose=False, train_test='train')
    test.start_game(verbose=False, train_test='test')

print('Train Win % = {0:.0%}'.format(sum(train.wins) / len(train.wins)))
print('Test Win % = {0:.0%}'.format(sum(test.wins) / len(test.wins)))
