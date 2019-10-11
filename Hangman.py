# -*- coding: utf-8 -*-
"""
Created on Wed Mar  6 22:59:42 2019

@author: galar
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Mar  6 16:45:01 2019

@author: galar
"""

import random
import collections
 
class HangmanAPI(object):
    def __init__(self):
        self.guessed_letters = []
        self.incorrect_guesses = []
        
        full_dictionary_location = "dictionaries/words_250000_train.txt"
        test_dictionary_location = "dictionaries/words_test.txt"
        self.full_dictionary = self.build_dictionary(full_dictionary_location)        
        self.test_dictionary = self.build_dictionary(test_dictionary_location)
                        
        self.letter_set = sorted(set("".join(self.full_dictionary)))
        
        self.probabilities = [0] * len(self.letter_set)
        
        self.unigram, self.bigram, self.trigram, self.fourgram, self.fivegram = self.build_n_grams(self.full_dictionary)
        
        self.tries_remaining = 6
        
        self.current_dictionary = []
        
        self.wins = []
        self.lose_words = []
        
    def guess(self, word): # word input example: "_ p p _ e "
        '''
        Given a word with either correctly gussed letters or blanks, this function
        returns the best guess for the next letter based on the n-grams
        '''
        
        # keep track of incorrect guesses to update the n-grams
        self.incorrect_guesses = list(set(self.guessed_letters) - set(word))
        
        # only recalibrate if last guess was incorrect and running low on guesses
        if len(self.guessed_letters) > 0 and self.guessed_letters[-1] in self.incorrect_guesses and self.tries_remaining <= 3:
            self.recalibrate_n_grams()
        
        # clear out probabilities from last guess
        self.probabilities = [0] * len(self.letter_set)

        # clean the word so that we strip away the space characters
        # replace "_" with "." as "." indicates any character in regular expressions
        clean_word = word[::2]
        
        # run through n-gram function
        return self.fivegram_probs(clean_word)
    
    
    def build_n_grams(self, dictionary):
        '''
        build nested dictionary containing occurences for n (1-5) sequences of letters
        unigrams and bigrams have an extra level for length of the word
        for unigram, take only unique letters within each word  
        '''
        unigram = collections.defaultdict(lambda: collections.defaultdict(int))
        bi_gram = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.defaultdict(int)))
        tri_gram = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.defaultdict(int)))
        four_gram = collections.defaultdict(lambda:collections.defaultdict(lambda: collections.defaultdict(lambda: collections.defaultdict(int))))
        five_gram = collections.defaultdict(lambda: collections.defaultdict(lambda:collections.defaultdict(lambda: collections.defaultdict(lambda: collections.defaultdict(int)))))
        
        # go through each word in the dictionary
        for word in dictionary:
            # check each letter in the dictionary and update the n-gram
            for i in range(len(word) - 4):
                bi_gram[len(word)][word[i]][word[i+1]] += 1
                tri_gram[word[i]][word[i+1]][word[i+2]] += 1
                four_gram[word[i]][word[i+1]][word[i+2]][word[i+3]] += 1
                five_gram[word[i]][word[i+1]][word[i+2]][word[i+3]][word[i+4]] += 1
            i = len(word) - 4
            
            # fill out the rest of the n-grams for words too short
            if len(word) == 2:
                bi_gram[len(word)][word[0]][word[1]] += 1
            elif len(word) == 3:
                bi_gram[len(word)][word[0]][word[1]] += 1
                bi_gram[len(word)][word[1]][word[2]] += 1
                tri_gram[word[0]][word[1]][word[2]] += 1
                
            # fill out rest of the (1-4)-grams
            elif len(word) >= 4:
                bi_gram[len(word)][word[i]][word[i+1]] += 1
                bi_gram[len(word)][word[i+1]][word[i+2]] += 1
                bi_gram[len(word)][word[i+2]][word[i+3]] += 1
                tri_gram[word[i]][word[i+1]][word[i+2]] += 1
                tri_gram[word[i+1]][word[i+2]][word[i+3]] += 1
                four_gram[word[i]][word[i+1]][word[i+2]][word[i+3]] += 1
            
            # fill out unigrams
            for letter in set(word):
                unigram[len(word)][letter] += 1
                    
        return unigram, bi_gram, tri_gram, four_gram, five_gram
                    
        
    def recalibrate_n_grams(self):
        '''
        re-tabulates the n-grams after eliminating any incorrectly guessed letters
        updates the dictionary to remove words containing incorrectly guessed letters
        '''
        # updates the dictionary to remove words containing incorrectly guessed letters
        new_dict = [word for word in self.full_dictionary if not set(word).intersection(set(self.incorrect_guesses))]
        self.unigram, self.bigram, self.trigram, self.fourgram, self.fivegram = self.build_n_grams(new_dict)

    
    def fivegram_probs(self, word):
        ''' 
        Input: the word in the "clean" format with no spaces and a '_' if letter has not been guessed
        Flow: uses tri-gram to calculate the probability of a certain letter appearing in a five-letter sequence for a word of given length
        Output: probabilities for each letter to be used in next level
        '''
                
        # vector of probabilities for each letter
        probs = [0] * len(self.letter_set)
        
        total_count = 0
        letter_count = [0] * len(self.letter_set)

        # traverse the word and find patterns that have three consecutive letters where one of them is blank
        for i in range(len(word) - 4):
                        
            # case 1: "letter letter letter letter blank"
            if word[i] != '_' and word[i+1] != '_' and word[i+2] != '_' and word[i+3] != '_' and word[i+4] == '_':
                anchor_letter_1 = word[i]
                anchor_letter_2 = word[i+1]
                anchor_letter_3 = word[i+2]
                anchor_letter_4 = word[i+3]
                
                # calculate occurences of "anchor_letter_1 anchor_letter_2 blank" and for each letter not guessed yet
                for j, letter in enumerate(self.letter_set):
                    if self.fivegram[anchor_letter_1][anchor_letter_2][anchor_letter_3][anchor_letter_4][letter] > 0 and letter not in self.guessed_letters:
                        total_count += self.fivegram[anchor_letter_1][anchor_letter_2][anchor_letter_3][anchor_letter_4][letter]
                        letter_count[j] += self.fivegram[anchor_letter_1][anchor_letter_2][anchor_letter_3][anchor_letter_4][letter]
        
            # case 2: "letter letter letter blank letter"
            elif word[i] != '_' and word[i+1] != '_' and word[i+2] != '_' and word[i+3] == '_' and word[i+4] != '_':
                anchor_letter_1 = word[i]
                anchor_letter_2 = word[i+1]
                anchor_letter_3 = word[i+2]
                anchor_letter_4 = word[i+4]
                
                # calculate occurences of "anchor_letter_1 blank anchor_letter_2" and for each letter not guessed yet
                for j, letter in enumerate(self.letter_set):
                    if self.fivegram[anchor_letter_1][anchor_letter_2][anchor_letter_3][letter][anchor_letter_4] > 0 and letter not in self.guessed_letters:
                        total_count += self.fivegram[anchor_letter_1][anchor_letter_2][anchor_letter_3][letter][anchor_letter_4]
                        letter_count[j] += self.fivegram[anchor_letter_1][anchor_letter_2][anchor_letter_3][letter][anchor_letter_4]
               
            # case 3: letter letter blank letter letter
            elif word[i] != '_' and word[i+1] != '_' and word[i+2] == '_' and word[i+3] != '_' and word[i+4] != '_':
                anchor_letter_1 = word[i]
                anchor_letter_2 = word[i+1]
                anchor_letter_3 = word[i+3]
                anchor_letter_4 = word[i+4]
                
                # calculate occurences of "blank anchor_letter_1 anchor_letter_2" and for each letter not guessed yet
                for j, letter in enumerate(self.letter_set):
                    if self.fivegram[anchor_letter_1][anchor_letter_2][letter][anchor_letter_3][anchor_letter_4] > 0 and letter not in self.guessed_letters:
                        total_count += self.fivegram[anchor_letter_1][anchor_letter_2][letter][anchor_letter_3][anchor_letter_4]
                        letter_count[j] += self.fivegram[anchor_letter_1][anchor_letter_2][letter][anchor_letter_3][anchor_letter_4]
               
            # case 4: letter blank letter letter letter
            elif word[i] != '_' and word[i+1] == '_' and word[i+2] != '_' and word[i+3] != '_' and word[i+4] != '_':
                anchor_letter_1 = word[i]
                anchor_letter_2 = word[i+2]
                anchor_letter_3 = word[i+3]
                anchor_letter_4 = word[i+4]
                
                # calculate occurences of "blank anchor_letter_1 anchor_letter_2" and for each letter not guessed yet
                for j, letter in enumerate(self.letter_set):
                    if self.fivegram[anchor_letter_1][letter][anchor_letter_2][anchor_letter_3][anchor_letter_4] > 0 and letter not in self.guessed_letters:
                        total_count += self.fivegram[anchor_letter_1][letter][anchor_letter_2][anchor_letter_3][anchor_letter_4]
                        letter_count[j] += self.fivegram[anchor_letter_1][letter][anchor_letter_2][anchor_letter_3][anchor_letter_4]
        
            # case 5: blank letter letter letter letter
            elif word[i] == '_' and word[i+1] != '_' and word[i+2] != '_' and word[i+3] != '_' and word[i+4] != '_':
                anchor_letter_1 = word[i+1]
                anchor_letter_2 = word[i+2]
                anchor_letter_3 = word[i+3]
                anchor_letter_4 = word[i+4]
                
                # calculate occurences of "blank anchor_letter_1 anchor_letter_2" and for each letter not guessed yet
                for j, letter in enumerate(self.letter_set):
                    if self.fivegram[letter][anchor_letter_1][anchor_letter_2][anchor_letter_3][anchor_letter_4] > 0 and letter not in self.guessed_letters:
                        total_count += self.fivegram[letter][anchor_letter_1][anchor_letter_2][anchor_letter_3][anchor_letter_4]
                        letter_count[j] += self.fivegram[letter][anchor_letter_1][anchor_letter_2][anchor_letter_3][anchor_letter_4]
        
        # calculate the probabilities of each letter appearing
        if total_count > 0:
            for i in range(len(self.letter_set)):
                probs[i] = letter_count[i] / total_count
        
        # interpolate probabilities between trigram and bigram
        for i, p in enumerate(self.probabilities):
            self.probabilities[i] = p + probs[i] * (0.40)
        
        # run the next level down
        return self.fourgram_probs(word)
    
    def fourgram_probs(self, word):
        ''' 
        Input: the word in the "clean" format with no spaces and a '_' if letter has not been guessed
        Flow: uses tri-gram to calculate the probability of a certain letter appearing in a four-letter sequence for a word of given length
        Output: probabilities for each letter to be used in next level
        '''
                
        # vector of probabilities for each letter
        probs = [0] * len(self.letter_set)
        
        total_count = 0
        letter_count = [0] * len(self.letter_set)

        # traverse the word and find patterns that have three consecutive letters where one of them is blank
        for i in range(len(word) - 3):
                        
            # case 1: "letter letter letter blank"
            if word[i] != '_' and word[i+1] != '_' and word[i+2] != '_' and word[i+3] == '_':
                anchor_letter_1 = word[i]
                anchor_letter_2 = word[i+1]
                anchor_letter_3 = word[i+2]
                
                # calculate occurences of "anchor_letter_1 anchor_letter_2 blank" and for each letter not guessed yet
                for j, letter in enumerate(self.letter_set):
                    if self.fourgram[anchor_letter_1][anchor_letter_2][anchor_letter_3][letter] > 0 and letter not in self.guessed_letters:
                        total_count += self.fourgram[anchor_letter_1][anchor_letter_2][anchor_letter_3][letter]
                        letter_count[j] += self.fourgram[anchor_letter_1][anchor_letter_2][anchor_letter_3][letter]
        
            # case 2: "letter letter blank letter"
            elif word[i] != '_' and word[i+1] != '_' and word[i+2] == '_' and word[i+3] != '_':
                anchor_letter_1 = word[i]
                anchor_letter_2 = word[i+1]
                anchor_letter_3 = word[i+3]
                
                # calculate occurences of "anchor_letter_1 blank anchor_letter_2" and for each letter not guessed yet
                for j, letter in enumerate(self.letter_set):
                    if self.fourgram[anchor_letter_1][anchor_letter_2][letter][anchor_letter_3] > 0 and letter not in self.guessed_letters:
                        total_count += self.fourgram[anchor_letter_1][anchor_letter_2][letter][anchor_letter_3]
                        letter_count[j] += self.fourgram[anchor_letter_1][anchor_letter_2][letter][anchor_letter_3]
               
            # case 3: letter blank letter letter
            elif word[i] != '_' and word[i+1] == '_' and word[i+2] != '_' and word[i+3] != '_':
                anchor_letter_1 = word[i]
                anchor_letter_2 = word[i+2]
                anchor_letter_3 = word[i+3]
                
                # calculate occurences of "blank anchor_letter_1 anchor_letter_2" and for each letter not guessed yet
                for j, letter in enumerate(self.letter_set):
                    if self.fourgram[anchor_letter_1][letter][anchor_letter_2][anchor_letter_3] > 0 and letter not in self.guessed_letters:
                        total_count += self.fourgram[anchor_letter_1][letter][anchor_letter_2][anchor_letter_3]
                        letter_count[j] += self.fourgram[anchor_letter_1][letter][anchor_letter_2][anchor_letter_3]
               
            # case 4: blank letter letter letter
            elif word[i] == '_' and word[i+1] != '_' and word[i+2] != '_' and word[i+3] != '_':
                anchor_letter_1 = word[i+1]
                anchor_letter_2 = word[i+2]
                anchor_letter_3 = word[i+3]
                
                # calculate occurences of "blank anchor_letter_1 anchor_letter_2" and for each letter not guessed yet
                for j, letter in enumerate(self.letter_set):
                    if self.fourgram[letter][anchor_letter_1][anchor_letter_2][anchor_letter_3] > 0 and letter not in self.guessed_letters:
                        total_count += self.fourgram[letter][anchor_letter_1][anchor_letter_2][anchor_letter_3]
                        letter_count[j] += self.fourgram[letter][anchor_letter_1][anchor_letter_2][anchor_letter_3]
        
        # calculate the probabilities of each letter appearing
        if total_count > 0:
            for i in range(len(self.letter_set)):
                probs[i] = letter_count[i] / total_count
        
        # interpolate probabilities between trigram and bigram
        for i, p in enumerate(self.probabilities):
            self.probabilities[i] = p + probs[i] * (0.25)
        
        # run the next level down
        return self.trigram_probs(word)

    def trigram_probs(self, word):
        ''' 
        Input: the word in the "clean" format with no spaces and a '_' if letter has not been guessed
        Flow: uses tri-gram to calculate the probability of a certain letter appearing in a three-letter sequence for a word of given length
        Output: probabilities for each letter to be used in next level
        '''
                
        # vector of probabilities for each letter
        probs = [0] * len(self.letter_set)
        
        total_count = 0
        letter_count = [0] * len(self.letter_set)

        # traverse the word and find patterns that have three consecutive letters where one of them is blank
        for i in range(len(word) - 2):
                        
            # case 1: "letter letter blank"
            if word[i] != '_' and word[i+1] != '_' and word[i+2] == '_':
                anchor_letter_1 = word[i]
                anchor_letter_2 = word[i+1]
                
                # calculate occurences of "anchor_letter_1 anchor_letter_2 blank" and for each letter not guessed yet
                for j, letter in enumerate(self.letter_set):
                    if self.trigram[anchor_letter_1][anchor_letter_2][letter] > 0 and letter not in self.guessed_letters:
                        total_count += self.trigram[anchor_letter_1][anchor_letter_2][letter]
                        letter_count[j] += self.trigram[anchor_letter_1][anchor_letter_2][letter]
        
            # case 2: "letter blank letter"
            elif word[i] != '_' and word[i+1] == '_' and word[i+2] != '_':
                anchor_letter_1 = word[i]
                anchor_letter_2 = word[i+2]
                
                # calculate occurences of "anchor_letter_1 blank anchor_letter_2" and for each letter not guessed yet
                for j, letter in enumerate(self.letter_set):
                    if self.trigram[anchor_letter_1][letter][anchor_letter_2] > 0 and letter not in self.guessed_letters:
                        total_count += self.trigram[anchor_letter_1][letter][anchor_letter_2]
                        letter_count[j] += self.trigram[anchor_letter_1][letter][anchor_letter_2]
               
            # case 3: blank letter letter
            elif word[i] == '_' and word[i+1] != '_' and word[i+2] != '_':
                anchor_letter_1 = word[i+1]
                anchor_letter_2 = word[i+2]
                
                # calculate occurences of "blank anchor_letter_1 anchor_letter_2" and for each letter not guessed yet
                for j, letter in enumerate(self.letter_set):
                    if self.trigram[letter][anchor_letter_1][anchor_letter_2] > 0 and letter not in self.guessed_letters:
                        total_count += self.trigram[letter][anchor_letter_1][anchor_letter_2]
                        letter_count[j] += self.trigram[letter][anchor_letter_1][anchor_letter_2]
        
        # calculate the probabilities of each letter appearing
        if total_count > 0:
            for i in range(len(self.letter_set)):
                probs[i] = letter_count[i] / total_count
        
        # interpolate probabilities between trigram and bigram
        for i, p in enumerate(self.probabilities):
            self.probabilities[i] = p + probs[i] * (0.20)
        
        # run the next level down
        return self.bigram_probs(word)
    
    
    def bigram_probs(self, word):
        ''' 
        Input: the word in the "clean" format with no spaces and a '_' if letter has not been guessed
        Flow: uses bi-gram to calculate the probability of a certain letter appearing in a two-letter sequence for a word of given length
              updates the probabilities set in trigram_probs
        Output: probabilities for each letter to be used in next level
        '''
        
        # vector of probabilities for each letter
        probs = [0] * len(self.letter_set)
        
        total_count = 0
        letter_count = [0] * len(self.letter_set)
        
        # traverse the word and find either patterns of "letter blank" or "blank letter"
        for i in range(len(word) - 1):
            # case 1: "letter blank"
            if word[i] != '_' and word[i+1] == '_':
                anchor_letter = word[i]
                
                # calculate occurences of "anchor_letter blank" and each letter not guessed yet
                for j, letter in enumerate(self.letter_set):
                    if self.bigram[len(word)][anchor_letter][letter] > 0 and letter not in self.guessed_letters:
                        total_count += self.bigram[len(word)][anchor_letter][letter]
                        letter_count[j] += self.bigram[len(word)][anchor_letter][letter]
                            
            # case 2: "blank letter"
            elif word[i] == '_' and word[i+1]!= '_':
                anchor_letter = word[i+1]
                
                # calculate occurences of "blank anchor_letter" and each letter not guessed yet
                for j, letter in enumerate(self.letter_set):
                    if self.bigram[len(word)][letter][anchor_letter] > 0 and letter not in self.guessed_letters:
                        total_count += self.bigram[len(word)][letter][anchor_letter]
                        letter_count[j] += self.bigram[len(word)][letter][anchor_letter]
                                                                    
        # calculate the probabilities of each letter appearing
        if total_count > 0:
            for i in range(len(self.letter_set)):
                probs[i] = letter_count[i] / total_count

        # interpolate probabilities between trigram and bigram
        for i, p in enumerate(self.probabilities):
            self.probabilities[i] = p + probs[i] * (0.10)
        
        # return letter associated with highest probability
        return self.unigram_probs(word)
    
    
    def unigram_probs(self, word):
        ''' 
        Input: the word in the "clean" format with no spaces and a '_' if letter has not been guessed
        Flow: uses unigram to calculate the probability of a certain letter appearing in a any blank space
              updates the probabilities set in bigram_probs
        Output: letter with the overall highest probability
        '''
                
        # vector of probabilities for each letter
        probs = [0] * len(self.letter_set)
        
        total_count = 0
        letter_count = [0] * len(self.letter_set)
        
        # traverse the word and find blank spaces
        for i in range(len(word)):
            # case 1: "letter blank"
            if word[i] == '_':
                                
                # calculate occurences of pattern and each letter not guessed yet
                for j, letter in enumerate(self.letter_set):
                    if self.unigram[len(word)][letter] > 0 and letter not in self.guessed_letters:
                        total_count += self.unigram[len(word)][letter]
                        letter_count[j] += self.unigram[len(word)][letter]
                       
        # calculate the probabilities of each letter appearing
        if total_count > 0:
            for i in range(len(self.letter_set)):
                probs[i] = letter_count[i] / total_count
                
        # interpolate probabilities
        for i, p in enumerate(self.probabilities):
            self.probabilities[i] = p + probs[i] * (0.05)
        
        # adjust probabilities so they sum to one (not necessary but looks better)
        final_probs = [0] * len(self.letter_set)
        if sum(self.probabilities) > 0:
            for i in range(len(self.probabilities)):
                final_probs[i] = self.probabilities[i] / sum(self.probabilities)
            
        self.probabilities = final_probs
        
        # find letter with largest probability
        max_prob = 0
        guess_letter = ''
        for i, letter in enumerate(self.letter_set):
            if self.probabilities[i] > max_prob:
                max_prob = self.probabilities[i]
                guess_letter = letter
        
        # if no letter chosen from above, pick a random one (extra weight on vowels)
        if guess_letter == '':
            letters = self.letter_set.copy()
            random.shuffle(letters)
            letters_shuffled = ['e','a','i','o','u'] + letters
            for letter in letters_shuffled:
                if letter not in self.guessed_letters:
                    return letter
            
        return guess_letter
        
  
    def build_dictionary(self, dictionary_file_location):
        text_file = open(dictionary_file_location,"r")
        full_dictionary = text_file.read().splitlines()
        text_file.close()
        return full_dictionary

                
    def start_game(self, actual_word=None, verbose=True, see_actual=False, train_test = 'train'):
        '''
        Plays a single game of hangman. Specify whether or not to use a word from the training
        dictionary or the test dictionary
        
        Parameters:
            actual_word: specify a word rather than use a random word from the dictionary
            verbose: print out the process throughout the game
            see_actual: preview the word before the game begins
            train_test: choose a random word from the training or test dictionary
        '''
        
        # reset guessed letters to empty set and current plausible dictionary to the full dictionary
        self.guessed_letters = []
        self.incorrect_guesses = []
        self.probabilities = [0] * len(self.letter_set)
        self.tries_remaining = 6
        self.recalibrate_n_grams()
                 
        if not actual_word:
            if train_test == 'train':
                actual_word = random.choice(self.full_dictionary)
            else:
                actual_word = random.choice(self.test_dictionary)
        
        if verbose and see_actual:
            print('The word is {}'.format(actual_word))
            
        characters = [i for i in actual_word]
        
        masked = ['_' for letter in characters]
    
        word = ' '.join(masked)
    
        while self.tries_remaining > 0:
            
            if verbose:
                print("{} tries remaining".format(self.tries_remaining))
                
                print(word)
                print('\n')
            
            my_guess = self.guess(word)
            
            self.guessed_letters.append(my_guess)
            
            if verbose:
                print("The letter {} is guessed".format(my_guess))
                print('\n')
        
            if my_guess in characters:
                indices = [i for i, x in enumerate(characters) if x == my_guess]
                
                for index in indices:
                    masked[index] = my_guess
                    
                word = ' '.join(masked)
                
                if '_' not in word:
                    if verbose:
                        print(word)
                        print('You win!')
                    self.wins.append(1)
                    break
    
            else:
                if verbose:
                    print("Bad guess")
                    print('\n')
                self.tries_remaining = self.tries_remaining - 1
                
        if '_' in word:
            if verbose:
                print("You lose!")
            self.wins.append(0)
            self.lose_words.append(actual_word)