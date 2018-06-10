import requests, os, errno, argparse
from htmlParser import HTMLTokenizer
from urlparse import urlparse

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

	# remove arguments, fragments etc
	def normalizeUrl(self, url):
		parts = urlparse(url)
		url = ''
		if len(parts.scheme) > 0:
			url = parts.scheme + '://'
		url += parts.netloc + parts.path
		return url

	def crawl(self, url):
		url = self.normalizeUrl(url)
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
			if url[-1] == '/':
				url = url[:-1]
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
				link = self.normalizeUrl(link)
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

def main():
	global CORPUS_DIR
	parser = argparse.ArgumentParser()
	parser.add_argument("base", help="base domain for crawling")
	parser.add_argument("-d", "--dir", help="directory name to write text corpus")
	parser.add_argument("-u", "--url", help="url to start crawling")
	args = parser.parse_args()
	if args.dir is not None:
		CORPUS_DIR = args.dir
	if args.base is None:
		print "Error: need to specify base domain"
		return
	if args.base[-1] != '/':
		args.base += '/'

	if args.url is None:
		args.url = args.base

	crawler = HttpCrawler(args.base)
	crawler.crawl(args.url)

if __name__ == "__main__":
    main()
