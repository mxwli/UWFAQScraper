import duckdb
import re
from html.parser import HTMLParser

'''
takes scraped pages and extracts qna pairs
qna schema: (question string, answer string, source string, embedding float[50])
'''

class Chunker(HTMLParser):
	def __init__(self):
		self.totdata = []
		super(Chunker, self).__init__()
	def handle_starttag(self, tag, attrs):
		self.totdata += [('start', tag)]
	def handle_endtag(self, tag):
		self.totdata += [('end', tag)]
	def handle_data(self, data):
		self.totdata += [('data', data)]

class HTMLTree:
	def buildNode(self):
		assert self.chunks[-1][0] == 'start'
		ret = {'type': self.chunks.pop()[1], 'children':[]}
		while len(self.chunks) > 0:
			if self.chunks[-1][0] == 'data':
				dat = self.chunks.pop()[1].strip()
				if len(dat) > 0:
					ret['children'] += [dat]
			elif (self.chunks[-1][0] == 'start'):
				ret['children'] += [self.buildNode()]
			else:
				self.chunks.pop()
				break
		return ret

	def __init__(self, chunks):
		self.chunks = list(reversed(chunks))
		self.tree = {'type': 'root', 'children': []}
		while len(self.chunks) > 0:
			if self.chunks[-1][0] == 'start':
				self.tree['children'] += [self.buildNode()]
			elif self.chunks[-1][0] == 'data':
				dat = self.chunks.pop()[1].strip()
				if len(dat) > 0:
					self.tree['children'] += [dat]
			else:
				self.chunks.pop()

def parseHTML(text):
	c = Chunker()
	c.feed(text)
	return HTMLTree(c.totdata).tree

def cleanHeader(header):
	header = header.replace(u'\xa0', ' ')
	return header.strip().replace('\n', ' ')

def cleanParagraph(par):
	par = par.replace(u'\xa0', ' ')
	return par.strip().replace('\n', ' ')

def getFlattenedContent(tree):
	contents = []
	for i in tree['children']:
		if type(i) is str:
			contents.append(i)
		else:
			contents.append(getFlattenedContent(i))
	return ' '.join(contents)

def isPossibleQuestion(text):
	flag = text.endswith("?")
	for word in 'who what where when why how'.split():
		flag = flag or text.lower().startswith(word)
	return flag

def isPossibleFaqPage(url, text):
	tmp = text.lower()
	return 'faq' in url or 'asked' in url or 'faq' in tmp or 'frequently asked questions' in tmp

def seekQNAPairs(tree):
	ret = []
	seeking = 'none'
	curQ = ''
	curA = []
	for ch in tree['children']:
		if type(ch) == str:
			continue
		if (seeking == 'none'):
			if re.fullmatch(r'h[1234]?|summary', ch['type']):
				content = cleanHeader(getFlattenedContent(ch))
				if (isPossibleQuestion(content)):
					seeking = 'header'
					curQ = content
		elif (seeking == 'header'):
			if ch['type'] in {'p', 'ul', 'ol'}:
				curA.append(cleanParagraph(getFlattenedContent(ch)))
			else:
				ret.append((curQ, '\n'.join(curA)))
				seeking = 'none'
				curQ = ''
				curA = []
		elif (seeking == 'summary'):
			if ch['type'] == 'div':
				curA.append(cleanParagraph(getFlattenedContent(ch)))
			ret.append((curQ, '\n'.join(curA)))
			seeking = 'none'
			curQ = ''
			curA = []

	if (len(ret) == 0):
		for ch in tree['children']:
			if type(ch) != str:
				ret += seekQNAPairs(ch)
	
	return ret

con = duckdb.connect(database = "persistent.duckdb", read_only = False)
alldata = con.execute("select * from pages").fetchall()

for url, text, hash in alldata:
	print(f"processing {url}")
	tree = parseHTML(text)
	pairs = seekQNAPairs(tree)
	print(f"found {len(pairs)} pairs in {url}\n")
	if len(pairs) >= 7 or isPossibleFaqPage(url, text):
		for q, a in pairs:
			con.execute("insert into qna (question, answer, source) values (?, ?, ?)",
				[q, a, url])
