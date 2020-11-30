# imports
# clean up imports
print('importing modules \n')
import re
import os
import time
import numpy
import pygame
import requests
import bs4 as bs
import urllib.request

from tkinter import *
from gtts import gTTS
from io import BytesIO
from mutagen.mp3 import MP3
from PIL import Image, ImageTk
from multiprocessing import Process
from gensim.summarization import summarize
from urllib.request import Request, urlopen

########################################################################################################################
articles = [['met','headline','article',-1,-1,'https://www.metoffice.gov.uk/weather/forecast/gcx4zrw25#?',''],
            ['bbc','headline','article',-1,-2,'https://www.bbc.co.uk/news/technology',''],
            ['net','headline','article',-1,9,'https://www.netblocks.org/reports',''],
            ['nyt','headline','article',-1,19,'https://www.nytimes.com/section/technology','https://www.nytimes.com'],
            ['mit','headline','article',-1,13,'https://www.technologyreview.com',''],
            ['reu','headline','article',-1,98,'https://uk.reuters.com/news/technology','https://uk.reuters.com'],
            ['ver','headline','article',-1,88,'https://www.theverge.com/tech',''],
            ['wir','headline','article',-1,39,'https://www.wired.com/','https://www.wired.com'],
            #['blo','headline','article',-1,-3,'https://www.bloomberg.com/technology','https://www.bloomberg.com'],
            ['hac','headline','article',-1,34,'https://www.hackster.io/news?ref=topnav','']]

images =    [['smith','caption','image',-1,4,'https://www.smithsonianmag.com/photocontest/photo-of-the-day'],
             ['nasa','caption','image',-1,0,'https://earthobservatory.nasa.gov/topic/image-of-the-day']]

########################################################################################################################
# pydoc functions
def txt_to_mp3(headline, name):
    """
        Takes the string 'headline' and converts it to speech using gTTS.
        Then saves the speech as a .mp3 file with the title 'name'.
        Args:
            headline: a string containing the scrapped news article
            name: the three letter string identifying the site the article was scrapped from
        Returns:
            audio.info.length: the float value of the time(in seconds)taken to play the .mp3 file
    """
    # converts the string 'headline' to an mp3 file saved as {name}.mp3 using gtts
    myobj = gTTS(text = headline, lang = 'en', slow = False)
    myobj.save('mp3/{}.mp3'.format(name))
    audio = MP3('mp3/{}.mp3'.format(name))
    print(name, audio.info.length)
    return(audio.info.length)

def speak(name, t):
    """
        Plays {name}.mp3 file for 't' seconds using pygame
        Args:
            name: the three letter string identifying the site the article was scrapped from
            t: the float value representing the lenght of time needed to play the .mp3 file
    """
    # loads {name}.mp3 and plays it for t seconds using pygame
    t = (t + 2)
    pygame.init()
    pygame.mixer.music.load('mp3/{}.mp3'.format(name))
    pygame.mixer.music.play()
    time.sleep(t)
    pygame.mixer.music.fadeout(0)
   
def sub_scrape(webpage):
    """
        Scrapes the webpage for the article headline(contained in the <h1></h1> HTML tags)and
        the main article(contained in the <p></p> HTML tags) using request and beautiful soup.
        The main article is then converted into a 500 word maximum string by using gensim summarization
        Args:
            webpage: the string containing the URL of the webpage containing the article to be scraped
        Returns:
            headline: a string containing the article headline
            summary: a string with the <500 word summary of the article contents 
    """
    # scrapes the webpage for the article and removes unnecessary details
    #print('scraping - ',webpage)
    req = Request(webpage, headers={'User-Agent':'Mozilla/5.0'})
    webpage = urlopen(req).read()
    soup = bs.BeautifulSoup(webpage,'lxml')

    headline = soup.find('h1').get_text()
    p_tags = soup.find_all('p')
    p_tags_text = [tag.get_text().strip() for tag in p_tags]

    sentence_list = [sentence for sentence in p_tags_text if not '\n' in sentence]
    sentence_list = [sentence for sentence in sentence_list if '.' in sentence]
    article = ' '.join(sentence_list)

    while len(article) > 500:
        article = summarize(article, ratio = 0.9)
    summary = headline + article
    return (headline, summary)


def scrape(webpage, linkNumber, extention):
    """
        scrapes the main page of a news website using request and beautiful soup and
        returns the URL link to the top article as a string
        Args:
            webpage: a string containing the URL of the main website
            linkNumber: an integer pointing to the URL of the top article from the list
            of all the URL's that have been scrapped
            extention: a string containing the suffix of the URL to be sent to the
            function sub_soup()
        returns:
            headline: a string containing the 500 word summary of the scrapped article
    """
    # returns the link to the top headline link
    req = Request(webpage, headers={'User-Agent':'Mozilla/5.0'})
    webpage = urlopen(req).read()
    soup = bs.BeautifulSoup(webpage,'lxml')

    link = soup.find_all('a')
    if linkNumber > 0:
        story = (link[linkNumber])
        sub_soup = str(extention + '{}'.format(story['href']))
    elif linkNumber == -1:
        sub_soup = articles[0][5]
    elif linkNumber == -2:
        link = soup.find('a',{'class':'gs-c-promo-heading'})
        sub_soup = 'https://www.bbc.co.uk{}'.format(link['href'])

    headline = sub_scrape(sub_soup)
    return headline

########################################################################################################################
def update_articles():
    """
        goes throught the 'articles' list and scrapes each website for the headline by calling the
        scrape() function. Then converts the headline to speech in a .mp3 file by calling  the txt_to_mp3()
        function. It attempt this five times as gTTS can sometimes be problematic. The 'articles' list is
        updated with the subsequent objects.
    """
    for article in range(0, len(articles)):
        # scrape headline, article
        print('\nscraping ', articles[article][0])
        articles[article][1], articles[article][2] = scrape(articles[article][5], articles[article][4], articles[article][6])

        # convert to mp3
        print('converting ',articles[article][0],' to mp3')
        attempts = 1
        while articles[article][3] <= 0 and attempts <= 5:
            try:
                articles[article][3] = txt_to_mp3(articles[article][2], articles[article][0])
            except:
                print('attempt ',attempts,'/5 unsuccessful')
                attempts += 1
            
########################################################################################################################
def clean_img(img):
    """
        takes the scrapped 'img' binary object and resizes it before converting it into the
        correct format to be displayed in TKinter
        Args:
            img: the binary object containing the scrapped image
        returns:
            im: the cleaned up image object
    """
    url = img
    response = requests.get(img)
    im1 = Image.open(BytesIO(response.content))    
    im_small = im1.resize((int(2*(screen_width)/3), int(3*(screen_height)/5)), Image.ANTIALIAS)
    im = ImageTk.PhotoImage(im_small)
    return im


def update_images():
    """
        goes through the 'images' list and scrappes the images using request and beautiful
        soup. the captions are also scrapped and converted to .mp3 files using the
        function txt_to_mp3(). If the image can't be scrapped, a generic image is used instead.
        The 'images' list is updated with the captions and image objects
    """
    for image in range(0, len(images)):
        try:
            print('\n scraping ', images[image][0])
            req = Request(images[image][5], headers={'User-Agent':'Mozilla/5.0'})
            webpage = urlopen(req).read()
            soup = bs.BeautifulSoup(webpage,'lxml')

            if images[image][0] == 'smith':
                try:
                    caption = soup.find('p', {'class' : 'photo-contest-detail-caption'})
                    caption = caption.text
                except:
                    caption = 'caption not found'
            else:
                try:
                    link = soup.find_all('a')
                    story = link[44]
                    sub_soup = 'https://earthobservatory.nasa.gov{}'.format(story['href'])
                    caption = str(sub_scrape(sub_soup))
                except:
                    caption = 'caption not found'

            img = soup.find_all('img', {'src':re.compile('.jpg')})
            img = img[images[image][4]]
            img = img['src']
            img = clean_img(img)
    
        except:
            # displays a generic image if unable to scrape
            caption = "unavailable"
            img = "https://images.unsplash.com/photo-1494548162494-384bba4ab999?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&w=1000&q=80"
            img = clean_img(img)
        finally:
            images[image][1] = caption
            images[image][2] = img
            attempts = 1
            while attempts <= 5 and images[image][3] < 0: 
                try:
                    images[image][3] = txt_to_mp3(images[image][1], images[image][0])
                except:
                    print('attempt ',attempts,'/5 unsuccessful')
                    attempts += 1   
             

def switch_img(img):
    """
        switches the image displayed on the TKinter window and the caption to match the image
        Args:
            img: the image object
        Returns:
            url: the updated image object
    """
    if img == images[0][2]:
        cap_widget.config(text = 'Nasa: {}'.format(images[1][1]), command=lambda:speak('{}'.format(images[1][0]), images[1][3]))        
        image_button.config(image = images[1][2])
        url = images[1][2]
       
    elif img  == images[1][2]:
        cap_widget.config(text = 'Smithsonian: {}'.format(images[0][1]), command=lambda:speak('{}'.format(images[0][0]), images[0][3]))            
        image_button.config(image = images[0][2])
        url = images[0][2]
    return(url)

########################################################################################################################

# TKINTER
root = Tk()

# getting screen's dimensions in pixels
screen_height = (root.winfo_screenheight()  -50)
screen_width = root.winfo_screenwidth()

# getting current news headlines and images of the day
update_articles()
update_images()

# widgets
widget = []
for article in range(0, len(articles)):
    widget.append(Button(root, wraplength=((screen_width)/3), command=lambda article=article:speak(articles[article][0], articles[article][3]), text = '{}'.format(articles[article][0]) +': {}'.format(articles[article][1]), bg='#49A', activebackground='#49F', font=("Helvetica", 16)))
    widget[article].place(x=0, y=((article)*((screen_height)/len(articles))), width= ((screen_width)/3), height=((screen_height)/len(articles)))

# image of the day display
cap_widget = Button(root, wraplength=(2*(screen_width)/3), command=lambda:speak('{}'.format(images[0][0]), images[0][3]), text = '{}'.format(images[0][0]) +': {}'.format(images[0][1]), bg='#49A', activebackground='#49F', font=("Helvetica", 16))
cap_widget.place(x=((screen_width)/3), y=(3*(screen_height)/5), width= (2*(screen_width)/3), height= (2*(screen_height)/5))  
url = images[0][2]
image_button = Button(root, image = (url), command=lambda:switch_img(url))
image_button.place(x=((screen_width)/3))

# styles
root.title("Morning headlines!")
root['bg'] = '#49A'
#root.attributes('fullscreen', True)
print("\n width x height = %d x %d (in pixels)\n" %(screen_width, screen_height))

# mainloop
mainloop()
input()
print('end')


