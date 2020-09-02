'''
Task: Web Scraping and Topic Identification
Date: 02/03/2019
'''

from bs4 import BeautifulSoup
import requests
import nltk
from nltk.stem.snowball import SnowballStemmer
import re 
from collections import Counter

class TopicAnalysis(object):
    '''
    Initialization
    - url(string): page url
    - soup(object): BeautifulSoup object
    - wordlist(list): list to store words extracted from the page
    - weights(dict): pre-defined weights for each tag
    '''
    def __init__(self, url):
        self.url = url
        self.soup = None
        self.wordlist = []
        self.weights = {
                            'title': 5,
                            'kw': 4,
                            'h': 3
                        }

    '''
    Request HTML page
    Exception handling
    '''
    def get_html(self):
        try:
            request = requests.get(self.url)
            request.raise_for_status()

        except requests.exceptions.RequestException as e:
            print("Error: ", e)
            exit(1)

        if request.status_code == 200:
            return request.text
        else:
            print("Error: ", e)
            exit(1)
            # return "{}"
        
    '''
    Use BeautifulSoup Library to parse web page
    Filter out <Script> & <Style> 
    Return BeautifulSoup object
    '''
    def parser(self):
        html = self.get_html()
        soup = BeautifulSoup(html, "html.parser")
        # extract Script & Style
        for script in soup(["script", "style"]):
            script.extract()
        self.soup = soup
        return soup    

    '''
    Use nltk Library to tokenize words
    Filter out stopwords
    Filter out non-letter words
    Word stemming
    Return modified word list
    '''
    def nltk(self, text):
        # load stopwords
        stopwords = nltk.corpus.stopwords.words('english')

        # tokenize words
        tokens = []
        text = text.lower()
        for sent in nltk.sent_tokenize(text):
            for word in nltk.word_tokenize(sent):
                if word not in stopwords:
                    tokens.append(word);  

        # filter out non-letter words
        filtered_tokens = []
        for token in tokens:
            if re.search('[a-zA-Z]', token):
                filtered_tokens.append(token)

        # word stemming
        stemmer = SnowballStemmer("english")
        stems = [stemmer.stem(t) for t in filtered_tokens]

        return stems


    '''
    Use BeautifulSoup Library to parse content from tags
    Parse title
    Parse meta keywords
    Parse headers
    Parse paragraph
    Prase article
    Apply weights and nltk to content
    Return modeified word list 
    '''
    def get_tags(self):

        # get title content
        title = self.soup.title or self.soup.find('title')
        if title:
            words = title.get_text()
            words *= self.weights['title']
            self.wordlist.extend(self.nltk(words))
        
        # get keywords
        kw = self.soup.find('meta', attrs={'name':'keywords'})
        if kw:
            kw = kw['content']
            words *= self.weights['kw']
            self.wordlist.extend(self.nltk(words))

        # get all h tags
        all_h = ""
        for h in self.soup.find_all('h1'):
            all_h += h.get_text()
            all_h += " "

        for h in self.soup.find_all('h2'):
            all_h += h.get_text()
            all_h += " "

        for h in self.soup.find_all('h3'):
            all_h += h.get_text()
            all_h += " "

        for h in self.soup.find_all('h4'):
            all_h += h.get_text()
            all_h += " "

        if all_h:
            words *= self.weights['h']
            self.wordlist.extend(self.nltk(words))

        # get all p tags
        all_p = ""
        for p in self.soup.find_all('p'):
            all_p += p.get_text()

        if all_p:
            self.wordlist.extend(self.nltk(all_p))

        # get article content
        all_a = ""
        for a in self.soup.find_all('article'):
            all_a += a.get_text()

        if all_a:
            self.wordlist.extend(self.nltk(all_a))

        return self.wordlist

        # print(self.wordlist)


    '''
    Calculate word density
    Print final result
    Return keywords
    '''
    def word_density(self):
        # Count total words
        total_words = len(self.wordlist)
        # Count words 
        count = Counter(self.wordlist)
        
        density = {}
        for key in count:
            density[key] = "{0:.2f}".format(float(count[key]/total_words)*100)
        
        # Sort words in decreasing order
        sorted_density = sorted(density.items(), key=lambda kv: kv[1], reverse=True)
        
        # Return words with density >= 1
        res = [ w for w in sorted_density if float(w[1]) >= 1 ]

        # Return top 10(or less) words
        keywords = [ i[0] for i in res[:10] ]
        
        print(keywords)
        return keywords

    '''
    Count word frequency
    No other usage
    '''
    def word_count(self):
        dic = {}
        for i in self.wordlist:
            if i not in dic:
                dic[i] = 1
            else:
                dic[i] += 1
        sorted_dic = sorted(dic.items(), key=lambda kv: kv[1], reverse=True)
        return sorted_dic[:5]

    '''
    Main function
    '''
    def main(self):
        self.parser()
        self.get_tags()
        self.word_density()

     
if __name__ == '__main__':
    url = input('Enter your page URL:')

    # URLs for testing purpose
    
    topic = TopicAnalysis(url)
    topic.main()

