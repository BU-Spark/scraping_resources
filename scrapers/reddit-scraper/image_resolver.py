'''
Contains rules to decide wether image is worth it or not.
'''

def parse_url(url):
	parsed = None
	if url.endswith('.jpg'):
		parsed = url
	elif 'imgur.com' in url:
		if '/a/' not in url and '/gallery/' not in url:
			parsed = 'http://i.imgur.com/{id}.jpg'.format(id=url.split('/')[-1])
	elif 'reddituploads.com' in url:
		parsed = url

	return parsed