# anagrams.py
# takes a list of words and finds all anagrams
#
# inputs:
#	-c, --ignore-capitals	If set, ignore capitalization
#	-m, --minletters :		Minimum number of letters for a word to be considered in anagram search.  Minimum is 2.  Default is 4.
#	-o, --output :			Text file to output anagrams to.  Will be overwritten if it already exists.
#	-p, --print :			If set, print list of anagrams to stdout.  If --output is not specified, this flag is set regardless.
#	-v, --verbose :			If set, make output verbose.
#	-x, --exclude-capitals	If set, exclude any capitalized words
#	-w, --wordlist :		Text file containing word list to analyze.  Can be space, tab, or newline separated.
#								If not found will search for system dictionary.
#
# System dictionaries searched for:
#	/usr/dict/words
#	/usr/share/dict/words
#
# basic algorithm:
# 	- read list of words from file
#	- sort the letters in each word
#	- sort the list of words, by comparison of the sorted letters
#	- iterate through sorted list, picking anagrams by blocks with same sorted letters
#
# assumptions:
#
#	- input is list of words containing only letters with whitespace characters (space, tab, newine) separating words
#	- words that are the same up to capitalization are considered anagrams, unless --discard-capitals is set

#################
# package imports
#################

import sys
import os
import string
import time
import argparse

###########
# constants
###########

# possible locations to find a system dictionary

system_dictionaries = ["/usr/dict/words", "/usr/share/dict/words"]

#################################
# function and class declarations
#################################

# printing function - keeps track of whether verbose or not
# saves code over having to check before every print

def printv(string):
	if verbose:
		print(string)

# class for keeping track of word with sorted letters
# need to include both sorted letters and original word, so need object with both

class anagram_word:
	
	# if word is "" create an empty word
	# empty word starts output loop
	# avoids having to compare to None in is_anagram_of()
	def __init__(self, word = ""):
		self.word = word
		# if applicable, get rid of any capitalization with lower()
		if ignore_capitals:
			word_to_sort = self.word.lower()
		else:
			word_to_sort = self.word
		# simplest letter sorting available
		# might not be the most efficient way to do this
		# this could be done without converting back to a string with join(), but the next step appears to take slightly longer in that case
		# resulting in longer overall time to run
		self.word_sorted = string.join(sorted(word_to_sort), "")
		self.len = len(self.word)
	
	def __len__(self):
		return self.len
	
	def __str__(self):
		return self.word
	
	def __eq__(self, other):
		return self.word == other.word
	
	def is_anagram_of(self, other):
		return self.word_sorted == other.word_sorted
	
	# this is where the actual comparison happens - one the letters are sorted, can compare words directly
	# python's native string comparison gives the desired result if the letters are sorted
	def compare(word1, word2):
		return cmp(word1.word_sorted, word2.word_sorted)
	
	# slower implementation that shows the comparison explicitly
	
	#def compare(word1, word2):
	#	# compare each letter
	#	for l1, l2 in zip(word1.word_sorted, word2.word_sorted):
	#		if l1 > l2: return 1
	#		elif l1 < l2: return -1
	#	return cmp(len(word1), len(word2))

###############
# start program
###############

# keep track of time taken to complete program

start_time = time.time()

print("\nanagrams.py - Anagram Finder\n")

# parse command line arguments

parser = argparse.ArgumentParser()
parser.add_argument("-w", "--wordlist", type=str, default=None, help="Text file containing word list to analyze.  If not specified, will search for system dictionaries in common locations.")
parser.add_argument("-o", "--output", type=str, default=None, help="Text file to write output to.")
parser.add_argument("-m", "--minletters", type=int, default=4, help="Minimum number of letters in a word for it to be considered for anagram search.  Minimum is 2.  Default is 4.")
parser.add_argument("-c", "--ignore-captials", dest="ignore_capitals", action="store_true", help="If set, ignore capitalization (words that differ by capitalization will be considered anagrams.  Has no effect if -i, --exclude-capitals is set.")
parser.add_argument("-x", "--exclude-capitals", dest="exclude_capitals", action="store_true", help="If set, discard any capitalized words (proper names).")
parser.add_argument("-p", "--print", dest="print_output", action="store_true", help="If set, print output of anagrams to stdout.  Set regardless if no -o, --output specified.")
parser.add_argument("-v", "--verbose", action="store_true", help="If set, make output verbose output.")

args = parser.parse_args()
wordlist_filename = args.wordlist
output_filename = args.output
min_letters = args.minletters
ignore_capitals = args.ignore_capitals
exclude_capitals = args.exclude_capitals
print_output = args.print_output
verbose = args.verbose

# check if minimum number of letters is >= 2

if min_letters < 2:
	raise Exception("The minimum number of letters must be at least two.")

# check if output file is valid

if output_filename:
	outbase, outf = os.path.split(output_filename)
	if (outbase != ""):
		if not os.path.isdir(outbase):
			raise IOError("The directory '{}' does not exist, so cannot write to '{}'.".format(outbase, outf))
	
	if os.path.isfile(output_filename):
		print("Warning: will overwrite {}".format(output_filename))
else:
	# if no output specified then print to stdout regardless of command line
	print_output = True

# search for system dictionaries if none specified

printv("Searching for word list...")

if not wordlist_filename:
	for sys_dict in system_dictionaries:
		if os.path.isfile(sys_dict):
			wordlist_filename = sys_dict
			printv("System dictionary found: {}".format(sys_dict))
			break
	
	# None specified and defaults not found
	if wordlist_filename == None:
		raise Exception("No word list specified and no system dictionary found.")
else:
	if not os.path.isfile(wordlist_filename):
		raise Exception("The specified word list path \"{}\" cannot be found.".format(wordlist_filename))

printv("Getting words...")

file = open(wordlist_filename)
words = file.read().split()

printv("Found {} words in word list.".format(len(words)))

#########
# sorting
#########

printv("Sorting letters in each word...")

anagram_words = []
for word in words:
	
	if len(word) < min_letters: continue
	# exclude capitalized words if applicable
	if exclude_capitals and word[0].isupper(): continue
	
	# create anagram_word which will sort letters in its constructor
	anagram_words.append(anagram_word(word))

# sort words by comparing sorted letters

printv("Sorting words...")

anagram_words.sort(cmp=anagram_word.compare)

########
# output
########

# have all anagrams together now, just iterate through list to find them

# if writing to file, use that file as the buffer, otherwise just use stdout
# if writing to file and to stdout, write to file then read contents

if output_filename:
	printv("Writing to file...")
	outbuf = open(output_filename, "w+")
else:
	printv("Printing anagrams...\n")
	outbuf = sys.stdout

# empty word starts loop
theword = anagram_word()
newword = True

# iterate through words, pick out blocks with the same sorted letters

for ang_word in anagram_words:
	if ang_word.is_anagram_of(theword):
		if newword:
			outbuf.write(str(theword))
			outbuf.write(", ")
			outbuf.write(str(ang_word))
			newword = False
		else:
			outbuf.write(", ")
			outbuf.write(str(ang_word))
	else:
		theword = ang_word
		if not newword:
			outbuf.write("\n")
		newword = True

# if output is file but still need to print to stdout, read from the file buffer

if output_filename:
	if (print_output):
		printv("Printing anagrams...\n")
		outbuf.seek(0)
		print(outbuf.read())
		print("")
	outbuf.close()
else:
	print("\n")

printv("Done.")
printv("Time taken: {} seconds.".format(time.time()-start_time))