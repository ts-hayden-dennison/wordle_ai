

import csv
import sys
from word_data import valid_guesses

freqs = []

for i in range(0, len(valid_guesses[0])):
	freqs.append({})
	for j in 'abcdefghijklmnopqrstuvwxyz':
		freqs[-1][j] = 0
	
	for word in valid_guesses:
		freqs[-1][word[i]] = freqs[-1][word[i]] + 1

total = len(valid_guesses)
normalfreqs = []
for place in freqs:
	normalfreqs.append({})
	for i in 'abcdefghijklmnopqrstuvwxyz':
		normalfreqs[-1][i] = 0
	for letter in place.keys():
		normalfreqs[-1][letter] = float(place[letter])/total

for i, place in enumerate(normalfreqs):
	with open('place{}.csv'.format(i), 'w', newline='') as f:
		writer = csv.writer(f)
		for letter in place.keys():
			writer.writerow([letter, place[letter]])

sys.exit()
#