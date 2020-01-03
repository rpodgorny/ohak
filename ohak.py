import pickle
import sys
import re
import unicodedata
import pprint


class color:
	PURPLE = '\033[95m'
	CYAN = '\033[96m'
	DARKCYAN = '\033[36m'
	BLUE = '\033[94m'
	GREEN = '\033[92m'
	YELLOW = '\033[93m'
	RED = '\033[91m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'
	END = '\033[0m'


DEBUG = 0
n_pred = 2

def norm(s):
	return unicodedata.normalize('NFKD', s).encode('ASCII', 'ignore').decode().lower()


#def purify_word(s):
#	return s.replace(' ', '').replace(',', '').replace('.', '').replace('-', '').replace('\n', '').replace('(', '').replace(')', '')


def purify_word(s):
	return re.sub('[^a-zA-ZáÁčČďĎéÉěĚíÍňŇóÓřŘšŠťŤúÚůŮýÝžŽ]', '', s)


def is_accented(s):
	return re.search('[áÁčČďĎéÉěĚíÍňŇóÓřŘšŠťŤúÚůŮýÝžŽ]', s)


def capitalize_by_original(s, s_orig):
	ret = ''
	while s:
		ret += s[0].upper() if s_orig[0].isupper() else s[0]
		s, s_orig = s[1:], s_orig[1:]
	return ret


def diff(s1, s2):
	ret = ''
	for i in range(len(s1)):
		if s1[i] != s2[i]:
			ret += color.RED
			ret += s1[i]
			ret += color.END
		else:
			ret += s1[i]
	return ret


def counts_for_pwe(w, pwe, d):
	ret = []
	for k, v in d[w].items():
		if pwe in v:
			ret.append((v[pwe], k))
	return ret


def ohak_one(w, w_pred, d):
	#print('OHAK_ONE', w, w_pred)
	if not purify_word(w):
		return w
	elif is_accented(w):
		return w
	elif norm(w) not in d:
		return w
	# TODO: add a single option fast path here
	else:
		w_win = w
		pwe = w_pred[-2:]
		#print('HNUS', w, pwe)
		#pprint.pprint(d[norm(w)])
		while 1:
			cands = sorted(counts_for_pwe(norm(w), pwe, d))
			#print('CANDS', norm(w), pwe, cands)
			if cands:
				winner = cands[-1][1]
				#print('WINNER', w, pwe, winner)
				w_win = capitalize_by_original(winner, w)
				break
			if not pwe:
				break
			pwe = pwe[1:]
		return w_win


def ohak(ws, d):
	ret = []
	for i in range(len(ws)):
		w = ws[i]
		ret_pur = list(filter(None, [purify_word(x).lower() for x in ret]))
		w_pred = ret_pur[-1] if ret_pur else ''
		w_ohak = ohak_one(w, w_pred, d)
		ret.append(w_ohak)
	return ret

#with open('dict.msgpack', 'rb') as f:
#	d = msgpack.load(f)
with open('dict.pickle', 'rb') as f:
	d = pickle.load(f)

if DEBUG:
	print('dict:', len(d))

pat = re.compile(r'(\W+)')

for line in sys.stdin.readlines():
	if DEBUG:
		sys.stdout.write('ORIG: %s' % line)
	words = pat.split(line)
	#s = ''.join((norm(w) for w in words))
	if DEBUG:
		sys.stdout.write('NORM: %s' % s)
	s = ''.join((word for word in ohak(words, d)))
	sys.stdout.write(s)
	if DEBUG:
		#sys.stdout.write('OHAK: %s' % s)
		sys.stdout.write('DIFF: %s' % diff(s, line))
