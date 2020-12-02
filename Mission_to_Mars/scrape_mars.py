from splinter import Browser
from bs4 import BeautifulSoup
import requests
import pymongo
import pandas as pd
import time


def init_browser():
    # @NOTE: Replace the path with your actual path to the chromedriver
    executable_path = {"executable_path": "chromedriver.exe"}
    return Browser("chrome", **executable_path, headless=False)


def newget_soup(url, browser):
    
    browser.visit(url)
    html=browser.html
    soup = BeautifulSoup(html, 'html.parser')
    return soup


def scrape_info():
    browser = init_browser()
    
    mars_data = {}

    url = 'https://mars.nasa.gov/news/'

    soup = newget_soup('https://mars.nasa.gov/news/', browser)
    

    try:
        for x in range(3):
            element = browser.is_element_present_by_tag('li', wait_time=30)
            print(element)
            if element:
                break
        results = soup.find('li', class_='slide')
        news_title = results.find('div', class_='content_title').a.text 
        news_para = results.find('div', class_='article_teaser_body').text       
    except AttributeError as e:    
        news_title = 'error: Tag was not found'
        news_para = 'error: Tag was not found'


    mars_data['Title'] = news_title
    mars_data['Paragraph'] = news_para


    #######------Feature Image - Mars-----------------------------------------------------

    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    soup = newget_soup('https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars', browser)


    browser.find_by_id('full_image').first.click()
    time.sleep(2)
    browser.links.find_by_partial_text('more info').first.click()
    time.sleep(1)

    soup = BeautifulSoup(browser.html,'html.parser')

    image_src = soup.find("img", class_="main_image")['src']
    print(image_src)

    featured_image_url = "https://www.jpl.nasa.gov" + image_src
    print(f' The featured image url is: {featured_image_url}')
   
    mars_data['feature_img_url'] = featured_image_url

    ######-------Mars Facts---------------------------------------------------


    url = 'https://space-facts.com/mars/'

    tables = pd.read_html(url)
    df=tables[0]
    df.columns= ['Description', 'Value']
    df.set_index(['Description'])
    facts_html=df.to_html(header=False, index=False)

    mars_data['facts'] = facts_html
 


#####------Mars Hemispheres---------------------------------------------------

    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'

    soup = newget_soup('https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars', browser)


    data = soup.find_all("div", class_="item")

    hemisphere_img_urls = []

    # loop through image data to find title and url info
    for d in data:
        
        title = d.find("h3").text
        
        img_url = d.a["href"]
        
        url = "https://astrogeology.usgs.gov" + img_url
        
        # use requests to get full images url 
        response = requests.get(url)
        
        # create soup object
        soup = BeautifulSoup(response.text,"html.parser")
        
        # find full image url
        new_url = soup.find("div", class_='downloads').li.a['href']
        
        # create full image url
        full_url = new_url
        

        #make a dict and append to the list
        hemisphere_img_urls.append({"title": title, "img_url": full_url})
        

    

    mars_data['hemisphere_image_urls'] = hemisphere_img_urls

    browser.quit()
    return mars_data
    

