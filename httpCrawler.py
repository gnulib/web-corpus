import requests, os, errno
from htmlParser import HTMLTokenizer

CORPUS_DIR='corpus'

class HttpCrawler():
	visited = None
	corpus = None
	baseUrl = None
	siteBase = None

	def __init__(self, baseUrl):
		self.visited = {}
		self.corpus = []
		self.baseUrl = baseUrl
		parts=baseUrl.split('/')
		if len(parts) >= 3:
			self.siteBase = parts[0] + '//' + parts[2]
		else:
			self.siteBase = baseUrl

		try:
			os.makedirs(CORPUS_DIR)
		except OSError as e:
			if e.errno != errno.EEXIST:
				raise


	def urlInBase(self, url):
		if len(url) < len(self.baseUrl):
			return False

		if url[:len(self.baseUrl)] != self.baseUrl:
			return False

		return True

	def buildCorpus(self, url):
		if not self.urlInBase(url):
			return
		if url in self.visited:
			self.visited[url] += 1
			return
		else:
			self.visited[url] = 1
			print 'Crawling: %s ...' % url

		tknzr = HTMLTokenizer()

		words, links = tknzr.parse(requests.get(url).text)
		with open(CORPUS_DIR + '/' + url.replace('/', '_'), 'w') as f:
			for word in words:
				self.corpus.append(word)
				f.write(word.encode('utf-8') + ' ')
				# if word in self.corpus:
				# 	self.corpus[word] += 1
				# else:
				# 	self.corpus[word] = 1
		for link in links:
			if len(link) == 0:
				# skip blank url
				continue
			if link[0] == '#':
				# skip fragment within the page
				continue
			# print 'Crawling: %s ...' % link
			if len(link) < len('http://') or link[:len('http://')] not in ['https:/', 'http://']:
				# append relative path to site's base url
				link = self.siteBase + link
			self.buildCorpus(link)

		return