#import dependencies

#to pull data out of HTML and XML files 
from bs4 import BeautifulSoup

#to pull data from the web
import requests

#to help you perform regular expressions
import re

#a wrapper for functions that already exist in python
#eg of such functions: +,-,*,/ etc
import operator

#to help parse data
#json is a format of calling data from the web
import json

#takes a list of lists and creates a nice, pretty table on the terminal
#has 1 function (as mentioned above only)
from tabulate import tabulate

#to import system calls
#in this case: what wikipedia article we want to get there from
import sys

#to import words that dont matter
from stop_words import get_stop_words

#get data from Wikipedia

#w/api.php - will access the api
#format = json (1st parameter)
#action = query (because we are querying the data from the web)
#list type = search (if you type a word eg bird, it will search all wikipedia articles related to bird) and will list them
#srsearch = *name of the article you want to search*
wikipedia_api_link = "https://en.wikipedia.org/w/api.php?format=json&action=query&list=search&srsearch="
wikipedia_link = "https://en.wikipedia.org/wiki/"

#getting the user input

#an error message because the length is too small
if(len(sys.argv)<2): #if length is small then print, 'enter a valid string'
    print('enter a valid string') 
    exit()
    
#get the search word  
#article to be searched for put in the string query variable
string_query = sys.argv[1] #1st parameter, hence [1]

if (len(sys.argv) > 2): #if length of the article is > 2 then search_mode is true
    search_mode = True #True means remove stopwords
else:
    search_mode = False
##python main.py *name of the artice* *yes or no*. Pull the top 20 words from the arcle. yes/no means do you want to remove the stop words? yes/no
#python main.py batman yes

def getWordList(url):
    word_list = []
    #raw data
    source_code = requests.get(url)
    #convert to text
    plain_text = source_code.text
    #lxml format
    soup = BeautifulSoup(plain_text,'lxml')

    #find the words in paragraph tag
    for text in soup.findAll('p'):
        if text.text is None:
            continue
        #content
        content = text.text
        #lowercase and split into an array
        words = content.lower().split()

        #for each word
        for word in words:
            #remove non-chars
            cleaned_word = clean_word(word)
            #if there is still something there
            if len(cleaned_word) > 0:
                #add it to our word list
                word_list.append(cleaned_word)

    return word_list


#clean word with regex
def clean_word(word):
    cleaned_word = re.sub('[^A-Za-z]+', '', word)
    return cleaned_word


def createFrequencyTable(word_list):
    #word count
    word_count = {}
    for word in word_list:
        #index is the word
        if word in word_count:
            word_count[word] += 1
        else:
            word_count[word] = 1

    return word_count

#remove stop words
def remove_stop_words(frequency_list):
    stop_words = get_stop_words('en')

    temp_list = []
    for key,value in frequency_list:
        if key not in stop_words:
            temp_list.append([key, value])

    return temp_list

#create our url
url = wikipedia_api_link + string_query

#in a try and except block, you try something and if it doesnt work you make an exception
try:
    #making a query
    #make a requests library to get a url
    #storing article in the response variable
    response = requests.get(url) 
    
    #using json to load the data from response
    #decoding the data because it is not in the correct format
    #utf-8 is the format that we want
    data = json.loads(response.content.decode('utf-8'))
    
    #format this data
    #wikipedia_page_tag stores the first tag
    wikipedia_page_tag = data['query']['search'][0]['title']
    
    #create our new url
    # we pull the data from the new url
    url = wikipedia_link + wikipedia_page_tag
    
    #to get the list of words from that page
    page_word_list = getWordList(url)
    
    #create a table of word counts
    page_word_count = createFrequencyTable(page_word_list) 
    
    #sort the words
    sorted_word_frequency_list = sorted(page_word_count.items(), key = operator.itemgetter(1), reverse=True)
    
    #remove stop words
    if(search_mode):
        sorted_word_frequency_list = remove_stop_words(sorted_word_frequency_list)
    
    #sum the total words to calculate the frequency
    total_words_sum = 0
    for key, value in sorted_word_frequency_list:
        total_words_sum = total_words_sum + value
    
    #getting top 20 words
    if len(sorted_word_frequency_list) > 20:
        sorted_word_frequency_list = sorted_word_frequency_list[:20]
        
    #create the final list that will contain our words + frequency count + percentage
    final_list = []
    for key, value in sorted_word_frequency_list:
        percentage_value = float(value * 100)/total_words_sum
        final_list.append([key, value, round(percentage_value, 4)])
    
    #printing the headers
    print_headers = ['Words', 'Frequency', 'Frequency Percentage']
    
    #print the table with tabulate
    print(tabulate(final_list, headers=print_headers, tablefmt='orgtbl'))

#throw an exception in case it breaks
except requests.exceptions.Timeout:
    print("The server didn't respond. Please, try again later.")


