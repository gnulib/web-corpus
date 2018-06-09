from HTMLParser import HTMLParser

# not a thread safe class
class HTMLTokenizer(HTMLParser):
	skippers = ['head', 'script', 'style', 'nav', 'form', 'select']
	def init(self):
		self.links = []
		self.words = []
		self.skip = 0

	def parse(self, html):
		self.init()
		self.feed(html)
		return self.words, self.links

	def handle_starttag(self, tag, attrs):
		# print "processing tag: '%s' with attrs: '%s'" % (tag, attrs)
		if tag in ['a', 'A']:
			for attr in attrs:
				if attr[0] == 'href':
					# print 'adding link: %s' % attr[1]
					self.links.append(attr[1])
				else:
					# print 'skipping attribute: %s' % attr[0]
					pass
		
		if tag in self.skippers:
			self.skip += 1

	def handle_endtag(self, tag):
		if tag in self.skippers:
			self.skip -= 1
		if self.skip < 0:
			self.skip = 0
		return

	def handle_data(self, data):
		if self.skip > 0:
			return
		words = data.split()
		for word in words:
			if word[-1] in [',', '.', '!', '?']:
				self.words.append(word[:-1])
				self.words.append(word[-1])
			else:
				self.words.append(word)

