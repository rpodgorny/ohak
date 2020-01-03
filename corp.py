#!/usr/bin/python

import gensim
import unicodedata
import random
import cytoolz as toolz
import pickle
import re


def slw(n, seq):
	yield from toolz.sliding_window(n, ([None] * (n - 1)) + seq)
	#for i in toolz.sliding_window(n, ([None] * (n - 1)) + seq):
	#	yield tuple(filter(None, i))

def slw2(n, seq):
	for i in toolz.sliding_window(n, ([None] * (n - 1)) + seq):
		yield tuple(filter(None, i))

def norm(s):
	return unicodedata.normalize('NFKD', s).encode('ASCII', 'ignore').decode()


def is_czech(s):
	return re.fullmatch('[a-zA-ZáÁčČďĎéÉěĚíÍňŇóÓřŘšŠťŤúÚůŮýÝžŽ]+', s)


def simplify(d):
	ret = {}
	for k, v in d.items():
		if len(v) == 1:
			kk = list(v.keys())[0]
			ret[k] = {kk: {'': v[kk]['']}}
		else:
			ret[k] = v
	return ret


def gen_endings(s):
	while s:
		yield s
		s = s[1:]


d = {}
n_pred = 1

fn = 'cswiki-latest-pages-articles.xml.bz2'
wiki = gensim.corpora.WikiCorpus(fn, lemmatize=False, dictionary={})
for i, text in enumerate(wiki.get_texts()):
	if i % 1000 == 0:
		print(i, len(d))
	for words in slw(2, text):
		prev_word, word = words
		prev_word = '' if not prev_word else prev_word
		prev_word = '' if not is_czech(prev_word) else prev_word
		if not is_czech(word):
			continue
		w = norm(word)
		if not w:
			continue
		if len(w) != len(word):
			continue
		if not w in d:
			#d[w] = {'options': {}, 'pwes': {}}
			d[w] = {}
		if word not in d[w]:
			d[w][word] = {}
		#d[w]['options'][word] = d[w]['options'].get(word, 0) + 1
		pwe_ = prev_word[-3:]
		while 1:
			#if pwe_ not in d[w]:
			#	d[w][pwe_] = {}
			d[w][word][pwe_] = d[w][word].get(pwe_, 0) + 1
			if not pwe_:
				break
			pwe_ = pwe_[1:]
		#print('TTT', d[w])

	if i and i % 10000 == 0:
		print('saving %s %s' % (i, len(d)))
		#with open('dict.msgpack', 'wb') as f:
			#msgpack.dump(d, f)
		dd = simplify(d)
		print('SIMP', len(d), len(dd))
		with open('dict.pickle', 'wb') as f:
			pickle.dump(dd, f)
		print('saved')
