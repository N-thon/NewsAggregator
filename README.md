# NewsAggregator

## Overview
Aggregates tech articles scraped form news websites and displays them in a GUI or email transcript. Perfect for getting up to speed on todays developments in the tech world and can easily be extended to include your interests. Works best in combination with scheduling to appear everytime you log on or at the beggining of every day.

## How it works
Uses beautiful soup to request the top article from a list of websites. These articles are then condensed using gensim summarization.

*newsAggregator_gui* - The articles are then converted to speech using gTTS and saved as .mp3 files. a basic Tkinter gui displays the headlines and image of the day. The article summaries are read out when clicked on. 

*newsAggregator_email* - The article summaries are sent from the users email address to recipient email addresses.

## How to use
You can run `newsAggregator_gui.py` from the get go, as long as dependencies are installed. Make sure you visit the sites beforehand and accept cookies/JavaScript/etc...

`newsAggregator_email.py` requires you to first run `setupEmail.py` and enter your Gmail address and password as well as the emails you wish to send the aggregated news articles to. These will be stored in a plain text file but your password will be hashed for greater security. `newsAggregator_email.py` can then be run without emails being entered every time, making scheduling simple.

## Requirements 
pygame, beautifulSoup, requests, gTTS, mutagen, gensim.
```
pip install pygame
pip install beautifulsoup4
pip install requests
pip install gTTS
pip install mutagen
pip install gensim
```

## Known problems
less secure app access has to be *enabled* in your Gmail account to run the email automation. This can be found in `Manage your google account -> Security -> Less secure app access`.
![Alt text](emailAccess.png?raw=true "Title")

Recipients should check for the email in spam. 

## Tested on 
Windows 10, Python 3.7, pygame 1.6, beautifulsoup 4.9, requests 2.24, gTTS 2.1, mutagen 1.45, gensim 3.8
