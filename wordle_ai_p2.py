#!/bin/python

import sys
#from termcolor import colored, cprint
import random
import argparse
import csv
from collections import defaultdict
from word_data import valid_guesses, valid_answers
from itertools import compress, count, starmap

def locate(iterable, pred=bool, window_size=None):
    """Yield the index of each item in *iterable* for which *pred* returns
    ``True``.
    *pred* defaults to :func:`bool`, which will select truthy items:
        >>> list(locate([0, 1, 1, 0, 1, 0, 0]))
        [1, 2, 4]
    Set *pred* to a custom function to, e.g., find the indexes for a particular
    item.
        >>> list(locate(['a', 'b', 'c', 'b'], lambda x: x == 'b'))
        [1, 3]
    If *window_size* is given, then the *pred* function will be called with
    that many items. This enables searching for sub-sequences:
        >>> iterable = [0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3]
        >>> pred = lambda *args: args == (1, 2, 3)
        >>> list(locate(iterable, pred=pred, window_size=3))
        [1, 5, 9]
    Use with :func:`seekable` to find indexes and then retrieve the associated
    items:
        >>> from itertools import count
        >>> from more_itertools import seekable
        >>> source = (3 * n + 1 if (n % 2) else n // 2 for n in count())
        >>> it = seekable(source)
        >>> pred = lambda x: x > 100
        >>> indexes = locate(it, pred=pred)
        >>> i = next(indexes)
        >>> it.seek(i)
        >>> next(it)
        106
    """
    if window_size is None:
        return compress(count(), map(pred, iterable))

    if window_size < 1:
        raise ValueError('window size must be at least 1')

    it = windowed(iterable, window_size, fillvalue=_marker)
    return compress(count(), starmap(pred, it))


letterfreqs = []
for i in range(0, len(valid_guesses[0])):
	letterfreqs.append({})
	with open('place{}.csv'.format(i), 'r') as f:
		reader = csv.reader(f)
		for row in reader:
			letterfreqs[-1][str(row[0])] = float(row[1])


#######
def zero():
	return 0
def color_word(word1, word2):
	# coloring word2 as if it were a guess for the answer of word1
	colors = ['green' if word2[i] == c else 'white' for i, c in enumerate(word1)]
	
	tested = []
	for i, c in enumerate(word2):
		if c not in tested:
			inds1 = set(locate(word1, lambda x: x == c))
			inds2 = set(locate(word2, lambda x: x == c))
			if not inds1.issubset(inds2):
				diff = inds2 - inds1
				for i in range(0, len(inds1)):
					try:
						colors[diff.pop()] = 'yellow'
					except KeyError:
						break
			tested.append(c)
	
	#colorword = ''
	#for i, c in enumerate(word2):
	#	colorword = colorword + colored(c, colors[i])
	#return colorword, colors
	return colors


def score_start(word1, word2):
	global letterfreqs
	score = [0 for i in range(0, len(word1))]
	for i, c in enumerate(word1):
		if word2[i] == c:
			score[i] = 1
		else:
			score[i] = letterfreqs[i][c]
	return score


def score_similarity(word1, word2):
	score = [0 for i in range(0, len(word1))]
	for i, c in enumerate(word1):
		if word2[i] == c:
			score[i] = 1
	return score



def score_freq(word):
	global letterfreqs
	score = []
	for i, l in enumerate(word):
		score.append(letterfreqs[i][l])
	return score



def get_ai_guess(guesses, colors, correct):
	# collect information
	correct_inds = {}
	tested_inds = {}
	disallowed_letters = set()
	for tryi, word in enumerate(guesses):
		for j, letter in enumerate(word):
			if colors[tryi][j] == 'green':
				if letter in correct_inds.keys():
					correct_inds[letter].add(j)
				else:
					correct_inds[letter] = set([j])
			elif colors[tryi][j] == 'yellow':
				if letter in tested_inds.keys():
					tested_inds[letter].add(j)
				else:
					tested_inds[letter] = set([j])
	for tryi, word in enumerate(guesses):
		for j, letter in enumerate(word):
			if colors[tryi][j] == 'white' and letter not in correct_inds.keys() and letter not in tested_inds.keys():
				disallowed_letters.add(letter)
	
	print 'known correct: {}'.format(correct_inds)
	print 'tested spots: {}'.format(tested_inds)
	print 'known incorrect: {}'.format(disallowed_letters)
	
	
	# find all possible answers with the given combination of green and yellow letters
	possible_answers = []
	cflag = False
	for word in valid_answers:
		cflag = False
		for i, letter in enumerate(word):
			letterinds = set(locate(word, lambda x: x == letter))
			if letter in disallowed_letters:
				cflag = True
				break
			if letter in correct_inds.keys():
				if not correct_inds[letter].issubset(letterinds):
					cflag = True
					break
			if letter in tested_inds.keys():
				if i in tested_inds[letter]:
					cflag = True
					break
		if not set(correct_inds.keys()).issubset(set(word)):
			continue
		if not set(tested_inds.keys()).issubset(set(word)):
			continue
		if not cflag:
			possible_answers.append(word)
	
	
	#print possible_answers
	largest = 0
	for word in possible_answers:
		if word in guesses:
			continue
		score = sum(score_freq(word))
		if score > largest:
			largest = score
			final_answer = word
	
	
	# find word that would give us the most information
	possible_guesses = []
	cflag = False
	for word in valid_answers:
		if word in possible_answers:
			continue
		cflag = False
		for i, letter in enumerate(word):
			if letter in tested_inds.keys():
				if i in tested_inds[letter]:
					cflag = True
					break
			if letter in disallowed_letters:
				cflag = True
				break
			if letter in correct_inds.keys():
				if i in correct_inds[letter]:
					cflag = True
					break
		if not cflag:
			possible_guesses.append(word)
	
	largest = 0
	final_guess = None
	for word in possible_guesses:
		if word in guesses:
			continue
		score = sum(score_freq(word))
		if score > largest:
			largest = score
			final_guess = word
	
	
	#print possible_guesses
	print 'possible answers: {}'.format(len(possible_answers))
	print 'possible guesses: {}'.format(len(possible_guesses))
	# if we have a good chance of getting the answer, try that. otherwise try to get more info
	if len(possible_answers) > len(possible_guesses) or len(guesses) == 5 or final_guess == None or len(possible_answers) < 4:
		return final_answer
	else:
		return final_guess
	


if __name__ == '__main__':
	
	parser = argparse.ArgumentParser(description='Have an AI guess the given word or a random word using Wordle rules while displaying its progress. Use -p/--play to just play Wordle.')
	parser.add_argument('-a', '--answer', help="The answer the bot will attempt to guess. Leave blank to generate a random word.", \
						required=False, default=None)
	parser.add_argument('-s', '--start', help='The starting word for the bot to use. Leave blank to calculate the optimal starting word.', \
						required=False, default=None)
	#parser.add_argument('-g', '--guess', required=False, help=argparse.SUPPRESS)
	parser.add_argument('-p', '--play', required=False, default=False, action='store_const', const=True, help='If this flag is present you can just play a Wordle game with a random answer.')
	parser.add_argument('-o', '--output', required=False, default='scorehistory.dat', help='Log file')
	args = parser.parse_args()
	######
	
	
	optimal = ''
	for place in letterfreqs:
		largest = 0
		addletter = 'a'
		for letter in place.keys():
			if place[letter] > largest:
				largest = place[letter]
				addletter = letter
		optimal = optimal + addletter
	
	
	
	
	if not args.play:
		if args.start == None:
			print 'optimal starting letter combo is {}'.format(optimal)
			largest = 0
			best_starting_word = ''
			for i in valid_guesses:
				score = score_start(optimal, i)
				if sum(score) > largest:
					largest = sum(score)
					best_starting_word = i
			#print(score_start(optimal, best_starting_word))
			#best_starting_word_c, colors = color_word(optimal, best_starting_word)
			print 'closest legal word to this is '
			print best_starting_word
			args.start = best_starting_word
		else:
			print 'using starting word {}'.format(args.start)
	
	
	
	
	if args.answer == None:
		args.answer = random.choice(valid_answers)
		if not args.play:
			print 'Picking random answer: {}'.format(args.answer)
	
	
	if not args.play:
		largest = 0
		best_word = ''
		for i in valid_guesses:
			if i == args.answer:
				continue
			score = score_start(args.answer, i)
			if sum(score) > largest:
				largest = sum(score)
				best_word = i
		#best_word_c, colors = color_word(args.answer, best_word)
		print 'best starting word for {} was '.format(args.answer)
		print best_word
	
	
	"""
	if not args.play:
		if args.guess:
			guess_word_c, colors = color_word(args.answer, args.guess)
			print 'score for {}: '.format(args.answer)
			print guess_word_c
			sys.exit()
	"""
	
	guesses = []
	guesses_colored = []
	scolors = []
	success = False
	while True:
		if len(guesses) >= 6:
			break
		#for word in guesses_colored:
		for word in guesses:
			print '\t'+word
		if args.play:
			print
			print
			guess = raw_input('Try {}, enter a guess: '.format(len(guesses)+1))
		else:
			if len(guesses) != 0:
				# have the AI show what it's doing
				#guess = random.choice(valid_guesses)
				guess = get_ai_guess(guesses, scolors, args.answer)
			else:
				guess = args.start
			print
			print
			print 'Try {}, enter a guess: {}'.format(len(guesses)+1, guess)
		if len(guess) == len(args.answer):
			if guess in valid_guesses:
				if guess not in guesses:
					if guess != args.answer:
						#color_guess, score = color_word(args.answer, guess)
						score = color_word(args.answer, guess)
						
						#guesses_colored.append(color_guess)
						
						guesses.append(guess)
						scolors.append(score)
						continue
					else:
						success = True
						break
				else:
					print 'Already used {}'.format(guess)
			else:
				print 'Not a valid word'
		else:
			print 'Guess must be {} letters long'.format(len(args.answer))
		
	if success:
		print 'Nice job, you guessed the answer {} in {} tries!'.format(args.answer, len(guesses)+1)
	else:
		print 'The answer was {}. Better luck next time!'.format(args.answer)
	with open(args.output, 'a') as f:
		writer = csv.writer(f)
		person = 'AI' if not args.play else 'human'
		writer.writerow([person, args.answer, len(guesses)+1])
	
	sys.exit()
#
