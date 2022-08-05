

import sys
from termcolor import colored, cprint
import random
import argparse
import csv
from more_itertools import locate
from collections import defaultdict
from word_data import valid_guesses, valid_answers


letterfreqs = []
for i in range(0, len(valid_guesses[0])):
	letterfreqs.append({})
	with open('place{}.csv'.format(i), 'r', newline='') as f:
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
	
	colorword = ''
	for i, c in enumerate(word2):
		colorword = colorword + colored(c, colors[i])
	return colorword, colors


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
	
	print('known correct: {}'.format(correct_inds))
	print('tested spots: {}'.format(tested_inds))
	print('known incorrect: {}'.format(disallowed_letters))
	# find all valid words with the given combination of green and yellow letters
	possible_guesses = []
	cflag = False
	for word in valid_guesses:
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
			possible_guesses.append(word)
	
	print(possible_guesses)
	largest = 0
	for word in possible_guesses:
		if word in guesses:
			continue
		score = sum(score_freq(word))
		if score > largest:
			largest = score
			final_guess = word
	print(score_freq(final_guess))
	return final_guess



if __name__ == '__main__':
	
	parser = argparse.ArgumentParser(description='Have an AI guess the given word or a random word using Wordle rules while displaying its progress. Use -p/--play to just play Wordle.')
	parser.add_argument('-a', '--answer', help="The answer the bot will attempt to guess. Leave blank to generate a random word.", \
						required=False, default=None)
	parser.add_argument('-s', '--start', help='The starting word for the bot to use. Leave blank to calculate the optimal starting word.', \
						required=False, default=None)
	parser.add_argument('-g', '--guess', required=False, help=argparse.SUPPRESS)
	parser.add_argument('-p', '--play', required=False, default=False, action='store_const', const=True, help='If this flag is present you can just play a Wordle game with a random answer.')
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
			print('optimal starting letter combo is {}'.format(optimal))
			largest = 0
			best_starting_word = ''
			for i in valid_guesses:
				score = score_start(optimal, i)
				if sum(score) > largest:
					largest = sum(score)
					best_starting_word = i
			#print(score_start(optimal, best_starting_word))
			best_starting_word_c, colors = color_word(optimal, best_starting_word)
			print('closest legal word to this is ', end='')
			print(best_starting_word_c)
			args.start = best_starting_word
		else:
			print('using starting word {}'.format(args.start))
	
	
	
	
	if args.answer == None:
		args.answer = random.choice(valid_answers)
		if not args.play:
			print('Picking random answer: {}'.format(args.answer))
	
	
	
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
		best_word_c, colors = color_word(args.answer, best_word)
		print('best starting word for {} was '.format(args.answer), end="")
		print(best_word_c)
	
	
	
	if not args.play:
		if args.guess:
			guess_word_c, colors = color_word(args.answer, args.guess)
			print('score for {}: '.format(args.answer), end="")
			print(guess_word_c)
			sys.exit()
	
	
	guesses = []
	guesses_colored = []
	scolors = []
	success = False
	while True:
		if len(guesses) >= 6:
			break
		print()
		for word in guesses_colored:
			print(word)
		
		if args.play:
			guess = input('Try {}, enter a guess: '.format(len(guesses)+1))
		else:
			if len(guesses) != 0:
				# have the AI show what it's doing
				#guess = random.choice(valid_guesses)
				guess = get_ai_guess(guesses, scolors, args.answer)
			else:
				guess = args.start
			print('Try {}, enter a guess: {}'.format(len(guesses)+1, guess))
		if len(guess) == len(args.answer):
			if guess in valid_guesses:
				if guess not in guesses:
					if guess != args.answer:
						color_guess, score = color_word(args.answer, guess)
						guesses_colored.append(color_guess)
						guesses.append(guess)
						scolors.append(score)
						continue
					else:
						success = True
						break
				else:
					print('Already used {}'.format(guess))
			else:
				print('Not a valid word')
		else:
			print('Guess must be {} letters long'.format(len(args.answer)))
	if success:
		print('Nice job, you guessed the answer {} in {} tries!'.format(args.answer, len(guesses)+1))
	else:
		print('The answer was {}. Better luck next time!'.format(args.answer))
	sys.exit()
#
													   
