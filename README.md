# Hangman-NLP

## Purpose

This code can play a game of hangman, given a word with blank spaces and 6 guesses (head, body, arms and legs) will return the best letter to guess.

## Methodology

To determine the best guess, the model uses [n-gram](https://en.wikipedia.org/wiki/N-gram) counts. N-grams are typically used to determine the likelihood of a word following another, but in this case we will use it for letters.

In this case, the model uses n-grams from 1 (unigram), 2 (bigram) up to 5 (five-gram). Five is the chosen cutoff because most 6 and above letter sequences begin to be just a chain of smaller sequences.

The model is trained on a dictionary of approximately 250,000 words. This dictionary is used to determine the n-gram frequencies. For example, the following structure for the bigram frequencies are:

* word length (n-gram frequencies depend on length of the word)
    * first letter
        * second letter
            * second letter frequency (this indicates how many letter1-letter2 sequences there are)
            
## Gameplay

You can start a game by either selecting a random word from the dictionary, or by passing your own word as a string. The word is then converted into blanks (underscores separated by spaces) and is fed to the model to guess the first letter. For example, "hangman" is converted to "_ _ _ _ _ _ _". Any correctly guessed letter will replace the underscore, and this new string is passed for the next guess.

This string is then passed over to find any potential n-grams. For example, a unigram can be where there is any single blank space (in the above example, that would be every single space). A bigram can be anywhere with a blank and a letter, no matter the order, meaning "letter-blank" is a bigram as is "blank-letter". Therefore a single blank space can be multiple n-grams. If the current status of the word is "g i _ h u b", the blank space is a unigram, bigram (for both "i _" and "_ h"), trigram ("g i _", "i _ h", "_ h u"), four-gram and five-gram.

For each blank, a vector of probabilities for each letter not yet guessed is tabulated by calculating the frequencies of each n-gram, with more weight given to larger n. The letter with the highest probability is taken.

To help make smarter guesses, the n-gram frequencies are recalibrated to remove counts for incorrectly guessed letters. This improves the frequency values only focusing on what letters are still possible to guess. However, this process makes the code runtime much longer, and therefore the recalibration only occurs if there are less than 3 guesses remaining.

## Test

As mentioned, the model is trained on a dictionary of approximately 250,000 words. On this trained set, the model is able to win games of hangman at a 65% rate.

This is on words that the model has already seen. To see how well it performs on completely new words, another dictionary of words is used to test. Even on this new set of words, the model has a success rate of around 50%. Not bad for a computer who doesn't actually know the English language!

Feel free to test on your own dictionary, or to enter words you can think of!
