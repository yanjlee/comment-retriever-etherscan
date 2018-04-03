#!/usr/bin/python2
from bs4 import BeautifulSoup
from disqusapi import DisqusAPI
import urllib
import json
import urllib2, cookielib
import cfscrape
import re


class EtherScrapper():
	""" Represents an object that scraps data from the web """
	def __init__(self, address):
		web_page = "http://etherscan.io/address/"
		self.address = web_page + address
	
	"""
	finds the script and returns a soup object
	"""
	def find_script(self):
		cfs = cfscrape.create_scraper()
		script = cfs.get(self.address).content
		soup = BeautifulSoup(script, "html.parser")
		return soup
	"""
	Returns a dictionary mapping key-value pairs that match with disqus url encoding
	"""
	def get_thread_info(self, soup):
		thread_info = ""
		for script in soup.find_all('script'):
			if script.get('type') != None and script.get('src') == None:
				thread_info = script.string
				break
		thread_info = thread_info.strip()
		arguments = thread_info.split(";")
		page_info = {}
		for type in arguments:
			if len(type) == 0:
				break
			type_name = re.sub('var', '', type)
			type_name= type_name.strip()
			pair = type_name.split('=')
			page_info[pair[0].strip()] = pair[1].strip()
		return page_info
	"""
	Returns label
	"""
	def get_address_label(self, soup, address):
		label = ""
		for span in soup.find_all('span'):
			if span.get('title') != None:
				if span['title'] == address:
					label = span.string
					break
		if label == "" or label == address:
			return "No available label as of yet"
		else:
			return label
	"""
	Finds a url where the comments are stored in html format by disqus. Employs some matching based on
	the appropriate link
	"""
	def get_disqus_comments(self, page_info):
		address = "https://disqus.com/embed/comments/?"
		base ='default'
		so = 'default'
		version = '341c6ac006cf1e349b79ef1033b8b11a'
		f = re.sub('\'', '', page_info['disqus_shortname'].lower()) #how it is represented in disqus
		t_i = re.sub('\'', '', page_info['disqus_identifier'])
		encode_url = urllib.quote_plus(re.sub('\'', '', page_info['disqus_url']))
		t_u = encode_url
		t_e = re.sub('\'', '', page_info['disqus_title'])
		t_d = 'Ethereum%20Accounts%2C%20Address%20and%20Contracts'
		t_t = re.sub('\'', '', page_info['disqus_title'])
		s_o = so + '#' + 'version=%s' % version
		url = address + ('base=%s' % base) + ('&f=%s' % f)+ ('&t_i=%s' % t_i) + ('&t_u=%s' % t_u)+ ('&t_e=%s' % t_e) + ('&t_d=%s' % t_d) + ('&t_t=%s' % t_t) + '&s_o=%s' % s_o
		cfs = cfscrape.create_scraper()
		comment_script = cfs.get(url).content
		comment_soup = BeautifulSoup(comment_script, "html.parser")
		return comment_soup
	"""
	Returns a list whose entries represent a map of the necessary data about each comment e.g username, link to the parent comment etc
	"""
	def streamLine_data(self, commentMapping):
		reduced_data = []
		for i in xrange (0, len(commentMapping)):
			inner_map = commentMapping[i]
			for key in inner_map:
				name = key.strip()
				data_cpy = {}
				if name == 'message' or name == 'author' or name == 'id' or name == "createdAt" or name == "parent":
					if name == "author":
						data_cpy['username'] = inner_map[key]['username']
					else:
						data_cpy[name] = inner_map[key]
					reduced_data.append(data_cpy)
		return reduced_data			
			
	"""
	Returns a list object of comments
	"""
	def get_comments(self, comment_soup):
		comments = comment_soup.find(id="disqus-threadData")
		comments = comments.string.strip()
		decoded =  json.loads(comments)
		comment_map = decoded['response']['posts']
		return self.streamLine_data(comment_map)
	
	"""
	Copies the contents to a file named Solution which now has both the structured and unstructured data
	"""
	def send_to_file(self, label, comments, file_name):
		with open(file_name, "w") as file:
			file.write("label : " + label)
			file.write("\n")
			for i in xrange(0, len(comments)):
				comment_map = comments[i]
				for key in comment_map:
					file.write(key + " : " + str(comment_map[key]))
					file.write("\n")		

if __name__ == "__main__":
	address = "0xab11204cfeaccffa63c2d23aef2ea9accdb0a0d5" # for testing purposes
	scrapper = EtherScrapper(address)
	soup = scrapper.find_script()
	label = scrapper.get_address_label(soup, address)
	dict_info = scrapper.get_thread_info(soup)
	comment_soup = scrapper.get_disqus_comments(dict_info)
	comments = scrapper.get_comments(comment_soup)
	scrapper.send_to_file(label, comments, "solution")
	
	
	
	
			
		