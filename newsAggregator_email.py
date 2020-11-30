# imports
# clean up imports
print('importing modules \n')
import re
import requests
import bs4 as bs
import urllib.request
from gtts import gTTS
import email, smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from cryptography.fernet import Fernet
from gensim.summarization import summarize
from urllib.request import Request, urlopen
from email.mime.multipart import MIMEMultipart

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

########################################################################################################################
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
    req = Request(webpage, headers={'User-Agent':'Mozilla/5.0'})
    webpage = urlopen(req).read()
    soup = bs.BeautifulSoup(webpage,'lxml')

    headline = soup.find('h1').get_text()
    p_tags = soup.find_all('p')
    p_tags_text = [tag.get_text().strip() for tag in p_tags]

    sentence_list = [sentence for sentence in p_tags_text if not '\n' in sentence]
    sentence_list = [sentence for sentence in sentence_list if '.' in sentence]
    article = ' '.join(sentence_list)

    # reduces article to 500 words or less
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

    # some articles require a different scraping process
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

########################################################################################################################

# COMPOSE EMAIL
update_articles()

# code from: https://towardsdatascience.com/email-automation-with-python-72c6da5eef52

# assign key email aspects to variables for easier future editing
subject = "Daily Headlines"
body = ""
for article in range(0, len(articles)):
    body += '\n\n{}'.format(articles[article][0]) +':\n {}'.format(articles[article][1]) +' - \n {}'.format(articles[article][2])
    
# reading encrypted password from file
with open('password.txt', 'rb') as f:
    send_email = f.readline()
    lines = f.read().splitlines()
    recieve_email = lines[:-1]
    password = lines[-1]

# decrypting password
with open("key.key", "rb") as f:
    key = f.read()
    
f = Fernet(key)
decrypted = f.decrypt(password)

recp_email = []
sender_email = (send_email).decode("utf-8")
for email in recieve_email:
    recp_email.append((email).decode("utf-8"))
password = (decrypted).decode("utf-8") 

# Create the email head (sender, receiver, and subject)
email = MIMEMultipart()
email["From"] = sender_email
email["Subject"] = subject
email.attach(MIMEText(body, "plain"))

#Create SMTP session for sending the mail
try:
    session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
    session.starttls() #enable security
    session.login(sender_email, password) #login with mail_id and password
    text = email.as_string()
    for recipient_email in recp_email:
        email["To"] = recipient_email 
        session.sendmail(sender_email, recipient_email, text)
    session.quit()
    print('\n--Mail Sent--')
except smtplib.SMTPAuthenticationError:
    print("\n Error: Run SetupEmail.py, ensure details are correct and \n enable \'less secure app access\' in your Google account settings!")
