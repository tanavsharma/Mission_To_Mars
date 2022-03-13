# Import Splinter, BeautifulSoup, and Pandas
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt
from webdriver_manager.chrome import ChromeDriverManager


def scrape_all():
    # Initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in a dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        "hemispheres": hemisphere(browser)
    }

    # Stop webdriver and return data
    browser.quit()
    return data


def mars_news(browser):

    # Scrape Mars News
    # Visit the mars nasa news site
    url = 'https://data-class-mars.s3.amazonaws.com/Mars/index.html'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')
        # Use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find('div', class_='content_title').get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()

    except AttributeError:
        return None, None

    return news_title, news_p


def featured_image(browser):
    # Visit URL
    url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None

    # Use the base url to create an absolute url
    img_url = f'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/{img_url_rel}'

    return img_url

def mars_facts():
    # Add try/except for error handling
    try:
        # Use 'read_html' to scrape the facts table into a dataframe
        df = pd.read_html('https://data-class-mars-facts.s3.amazonaws.com/Mars_Facts/index.html')[0]

    except BaseException:
        return None

    # Assign columns and set index of dataframe
    df.columns=['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)

    # Convert dataframe into HTML format, add bootstrap
    return df.to_html(classes="table table-striped")


#
def hemisphere(browser):

    # 1. Use browser to visit the URL 
    url = 'https://marshemispheres.com/'
    browser.visit(url)  

    # 2. Create a list to hold the images and titles.
    hemisphere_image_urls = []
    hemisphere_image_titles = []

    # Parse the data
    html = browser.html
    img_url_soup = soup(html, 'html.parser')

    # 3. Write code to retrieve the image urls and titles for each hemisphere.
    items = img_url_soup.find_all('div', class_='collapsible results')

    ## Gets us the names of the Hemis
    hemis_names = items[0].find_all('h3')

    for name in hemis_names:
        hemisphere_image_titles.append(name.text)
    
    ## Gets us the img urls of the Hemis
    hemis_images = items[0].find_all('a')
    for images in hemis_images:
        if(images.img):    
            img_url = "https://marshemispheres.com/" + images['href']
            hemisphere_image_urls.append(img_url)

    ## Getting the full img link of hemis by clicking on the sample button
    full_url = []
    for url in hemisphere_image_urls:
    
        # Step 1: visit each url in our array.
        browser.visit(url)
        html = browser.html
        img_soup = soup(html, 'html.parser')
    
        # Step 2: find all the tags, and img urls and save them to variable
        output = img_soup.find_all('img', class_='wide-image')
        path = output[0]['src']
        full_link = "https://marshemispheres.com/" + path
    
        ## Step 3: Append to database
        full_url.append(full_link)

    ## store everything a dictionary
    hemi_zip = zip(hemisphere_image_titles, full_url)
    hemisphere_image_urls = []
    for title, url in hemi_zip:
        hemi_dict = {}
        hemi_dict['title'] = title
        hemi_dict['url'] = url
        hemisphere_image_urls.append(hemi_dict)

    return hemisphere_image_urls


if __name__== "__main__":
    # If running as script, print scrapped data
    print(scrape_all())

