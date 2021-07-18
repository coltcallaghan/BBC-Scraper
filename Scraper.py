# Import dependencies
import pytest
import spacy
import datetime
import re
import en_core_web_sm
import json
from urllib.request import urlopen
from bs4 import BeautifulSoup
import requests
import json 

def bbc_scraper(url):

    # Get HTML from URL
    page = urlopen(url)
    html_bytes = page.read()
    html = html_bytes.decode("UTF-8")
    soup = BeautifulSoup(html, "html.parser")

    # Get title
    match_results = re.search("<title.*?>.*?</title.*?>", html, re.IGNORECASE)
    title = match_results.group()
    title = re.sub("<.*?>", "", str(soup.title))

    # Get date
    date_pattern = '"datePublished":".*?",'
    date_published = re.findall(date_pattern, html, re.IGNORECASE)
    date_published = datetime.datetime.strptime(date_published[0][17:27], '%Y-%m-%d')
    date = (f"{date_published.day} {date_published.strftime('%B')} {date_published.year}")

    # Get article
    article_pattern = '<p>.*?</p>'
    article = re.findall(article_pattern, html, re.IGNORECASE)
    for i in range(len(article)):
      article[i] = re.sub("<.*?>", "", article[i])
      article[i] = re.sub("&quot;", '"', article[i])
      article[i] = re.sub("&#x27", "'", article[i])
      article[i] = re.sub("@.*?}", "", article[i])
      article[i] = re.sub(";s", "s", article[i])
      article[i] = re.sub(".css.*?}", '', article[i])
      article[i] = re.sub("}", '', article[i])
      article[i] = re.sub("\\\\", '', article[i]) 
      article[i] = re.sub(".css-83cqas-RichTextContainer{color:#3F3F42;}.css-83cqas-RichTextContainer > *:not([hidden]):not(style) ~ *:not([hidden]):not(style){margin-top:1rem;}.css-14iz86j-BoldText{font-weight:bold;}", "", article[i])
    article_string = " ".join(article[:-2])

    #Trying anything to get "\\" out 
    encoded_string = article_string.encode("ascii", "ignore")
    decode_string = encoded_string.decode()

    my_dict = {
        "Title": title,
        "Date_Published": date,
        "Content": decode_string
        }
    # Content is correct in dict but not when in json
    print(my_dict)

    results_json =json.dumps(my_dict)


    return results_json


bbc_scraper("https://www.bbc.co.uk/news/uk-52255054")

def extract_entities(string):
 
    # Get input, make string, tokenzie, make lists
    nlp = en_core_web_sm.load()
    X = nlp(string)
    personList = []
    placeList = []
    organisationList = []

    # For word in string, check if Person, Place, Organisation. If yes put in relevent list
    for i in (X.ents):
      if i.label_ == 'PERSON':
        person_list.append(i.text)
      if i.label_ == 'GPE':
        place_list.append(i.text)
      if i.label_ == 'ORG':
        organisation_list.append(i.text)


    entities_json = json.dumps({'people':person_list, 'places':place_list, 'organisations':organisation_list})

    return entities_json
    
    
    ####################################################################
# Test cases

def test_bbc_scrape():
    results = {'URL': 'https://www.bbc.co.uk/news/uk-52255054',
                'Title': 'Coronavirus: \'We need Easter as much as ever,\' says the Queen',
                'Date_published': '11 April 2020',
                'Content': '"Coronavirus will not overcome us," the Queen has said, in an Easter message to the nation. While celebrations would be different for many this year, she said: "We need Easter as much as ever." Referencing the tradition of lighting candles to mark the occasion, she said: "As dark as death can be - particularly for those suffering with grief - light and life are greater." It comes as the number of coronavirus deaths in UK hospitals reached 9,875. Speaking from Windsor Castle, the Queen said many religions had festivals celebrating light overcoming darkness, which often featured the lighting of candles. She said: "They seem to speak to every culture, and appeal to people of all faiths, and of none. "They are lit on birthday cakes and to mark family anniversaries, when we gather happily around a source of light. It unites us." The monarch, who is head of the Church of England, said: "As darkness falls on the Saturday before Easter Day, many Christians would normally light candles together.  "In church, one light would pass to another, spreading slowly and then more rapidly as more candles are lit. It\'s a way of showing how the good news of Christ\'s resurrection has been passed on from the first Easter by every generation until now." As far as we know, this is the first time the Queen has released an Easter message. And coming as it does less than a week since the televised broadcast to the nation, it underlines the gravity of the situation as it is regarded by the monarch. It serves two purposes really; it is underlining the government\'s public safety message, acknowledging Easter will be difficult for us but by keeping apart we keep others safe, and the broader Christian message of hope and reassurance.  We know how important her Christian faith is, and coming on the eve of Easter Sunday, it is clearly a significant time for people of all faiths, but particularly Christian faith. She said the discovery of the risen Christ on the first Easter Day gave his followers new hope and fresh purpose, adding that we could all take heart from this.  Wishing everyone of all faiths and denominations a blessed Easter, she said: "May the living flame of the Easter hope be a steady guide as we face the future." The Queen, 93, recorded the audio message in the White Drawing Room at Windsor Castle, with one sound engineer in the next room.  The Palace described it as "Her Majesty\'s contribution to those who are celebrating Easter privately".  It follows a speech on Sunday, in which the monarch delivered a rallying message to the nation. In it, she said the UK "will succeed" in its fight against the coronavirus pandemic, thanked people for following government rules about staying at home and praised those "coming together to help others". She also thanked key workers, saying "every hour" of work "brings us closer to a return to more normal times".'}
    scraper_result = bbc_scraper('https://www.bbc.co.uk/news/uk-52255054')
    assert json.loads(scraper_result) == results


def test_extract_entities_amazon_org():
    input_string = "I work for Amazon."
    results_dict = {'people':[],
                    'places':[],  
                    'organisations': ['Amazon']
                    }
    extracted_entities_results = extract_entities(input_string)
    assert json.loads(extracted_entities_results) == results_dict


def test_extract_entities_name():
    input_string = "My name is Bob"
    results_dict = {'people':['Bob'],
                    'places':[],
                    'organisations': []
                    }
    extracted_entities_results = extract_entities(input_string)
    assert json.loads(extracted_entities_results) == results_dict
    
    
test_bbc_scrape()
test_extract_entities_amazon_org()
test_extract_entities_name()
