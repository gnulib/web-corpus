import requests, os, errno
from htmlParser import HTMLTokenizer

CORPUS_DIR='corpus'

class HttpCrawler():
	visited = None
	corpus = None
	baseUrl = None
	siteBase = None
	linkList = None

	def __init__(self, baseUrl):
		self.visited = {}
		self.corpus = []
		self.linkList = []
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

	def crawl(self, url):
		if not self.urlInBase(url):
			return
		if url in self.visited:
			self.visited[url] += 1
			return
		self.linkList = [url]
		self.visited[url] = 1
		self.buildCorpus()

	def buildCorpus(self):

		tknzr = HTMLTokenizer()

		while len(self.linkList) > 0:
			url = self.linkList[0]
			self.linkList = self.linkList[1:]
			print 'Crawling: %s ...' % url
			words, links = tknzr.parse(requests.get(url).text)
			with open(CORPUS_DIR + '/' + url.replace('/', '_'), 'w') as f:
				for word in words:
					# self.corpus.append(word)
					f.write(word.encode('utf-8') + ' ')
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
				if not self.urlInBase(link):
					continue
				if link in self.visited:
					self.visited[link] += 1
					continue
				else:
					# print 'Queuing: %s ...' % link
					self.visited[link] = 1
					self.linkList.append(link)
		return
