import pandas as pd 
from bs4 import BeautifulSoup

file = open("dreviews.htm", "r")
file = file.read()

phtml = BeautifulSoup(file, features='lxml')

m = phtml.body.find('div', attrs={'class': 'lister-list'}) #.text

all_reviews = m.findAll('div')

fin_ratings = []
fin_reviews = []
fin_titles = []

raw_reviews = m.findAll('div', attrs={'class': 'text'})
raw_reviews = [i.text.split('show-more__control">')[0] for i in raw_reviews]

# Out of 10
raw_ratings = phtml.body.findAll('span', attrs={'class': 'rating-other-user-rating'})
#raw_ratings = raw_ratings.body.findAll('span')
raw_ratings = [i.text.split('>')[0] for i in raw_ratings]
raw_ratings = [' '.join(i.split()) for i in raw_ratings]
raw_ratings = [i.split('/')[0] for i in raw_ratings]

raw_titles = phtml.body.findAll('a', attrs={'class': 'title'})
raw_titles = [i.text.split('t_urv">')[0] for i in raw_titles]
raw_titles = [' '.join(i.split()) for i in raw_titles]

df = pd.DataFrame()
df['title'] = raw_titles
df['review'] = raw_reviews

df.to_csv("savedreviews.csv")