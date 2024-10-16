import requests
import re
import time
import duckdb

'''
takes preexisting links from pages table and scrapes for more pages
stores both link and text

pages schema: (url varchar, text varchar, hash int128)
'''

def is_uwaterloo(text):
	if 'archive' in text or 'profile' in text or 'people' in text:
		return False
	return text.startswith("/") or (text.startswith('https://') and 'uwaterloo.ca' in text)

def process_href(text):
	text = text[text.find('"')+1:-1]
	if (text == ''):
		return 'https://uwaterloo.ca/'
	if text.startswith('/'):
		text = "https://uwaterloo.ca" + text
	if '?' in text:
		text = text[:text.find('?')]
	if text[-1] != '/':
		text += '/'
	return text

def process_loc(text):
	text = text[5:-6]
	if (text == ''):
		return 'https://uwaterloo.ca/'
	if text[-1] != '/':
		text += '/'
	return text

def get_text(url, con = None):
	if (con is not None):
		res = con.execute("select text from pages where url = ?", [url]).fetchall()
		if len(res) > 0:
			print("accessed persistent text storage")
			return res[0][0]
	try:
		r = requests.get(url)
	except:
		return ""
	if (r.status_code == 200):
		return r.text
	else:
		return ""

def get_links(url, text):
	sitemap = get_text(url+"sitemap.xml")
	if (sitemap != ""):
		return list(filter(is_uwaterloo, map(process_loc, re.findall(r"<loc>.*</loc>", sitemap))))
	else:
		return list(filter(is_uwaterloo, map(process_href, re.findall(r"<a +href=\"[^\"]*\"", text))))

con = duckdb.connect(database = "persistent.duckdb", read_only = False)
prv_urls = list(map(lambda x: x[0], con.execute("select url from pages").fetchall()))
visited = set(prv_urls)

print("1 for manual input, 2 for scraping")
___t = input()
while (___t == '1'):
	print("enter url")
	url = input()
	if (url == ''):
		print("empty url. terminating")
		exit(0)
	text = get_text(url, con)
	if (url not in visited):
		print("url unexplored. inserting.")
		con.execute("INSERT INTO pages VALUES (?, ?, ?)", [url, text, hash(url)])
		visited.add(url)

queue = set(zip(range(len(prv_urls)), prv_urls))
topiter = len(prv_urls) + 1
cnt = 2000 # number of new links to scrape
while len(queue) != 0:
	ID, url = next(iter(queue))
	print(url)
	queue.remove((ID, url))
	text = get_text(url, con)
	links = get_links(url, text)
	if url not in visited:
		con.execute("INSERT INTO pages VALUES (?, ?, ?)", [url, text, hash(url)])
		visited.add(url)
		cnt-=1
	if (cnt <= 0):
		break
	for i in links:
		if i not in visited:
			queue.add((topiter, i))
			topiter += 1

print(list(visited))


