"""
The idea for this webscraper is to find and download all of
towards datascience articles from a start date to end date,
I want to read their articles but I don't want to pay for membership

This will go to the towards datascience archive and go through every single day
of every month from the year selected and download the entire html file to a
database on my computer

TOOD:

1. Need to update bs4 to selenium because the sites are protected by javascript, RIPERONI
"""

#I am pretty sure I can to this with bs4 and not selenium // SAD DAYS I WAS SO HOPEFULL
#bs4 w/ requests should be faster

import os
import time
import string
import datetime
import bs4 #likely get rid of
import pathlib
import requests #likely get rid of
import pandas as pd
from selenium import webdriver #will be using a webdriver in firefox

def get_url(url):
    """
    Params: url : string

    returns a Requests object

    handles exceptions just in case the url cannot be found
    """
    page = requests.get(url)

    try:
        page.raise_for_status()
    except:
        print("Could not download from {}...check URL of website".format(url))

    return page

def get_date_list(date_from, date_end = datetime.datetime.now().strftime("%d-%m-%Y")):
    """
    params: date_from : string
            date_to : string
            put them in the format %d-%m-%Y

    returns a list of sites between date_from and date_to

    """
    date_from = datetime.datetime.strptime(date_from, "%d-%m-%Y")
    date_end = datetime.datetime.strptime(date_end, "%d-%m-%Y")

    return list(pd.date_range(date_from, date_end).date)

def request_articles_site(date):
    """
    params: date : datetime object

    Checks to see if the datetime is before datetime.now()
    It needs to be before now otherwise there won't be a page to load

    This function gets the website which has the list of articles from date
    get_all_articles will iterate through each article from this page

    returns a bs4 object
    """

    if date > datetime.datetime.now().date():
        print("the date is greater than today, which means there are no articles")
        print("Exiting......")
        time.sleep(1)
        raise SystemExit

    url = "https://towardsdatascience.com/archive/{}".format(date.strftime("%Y/%m/%d"))

    page = get_url(url)

    return bs4.BeautifulSoup(page.text, "html.parser")


def get_all_articles(soup):
    """
    params: soup : BeautifulSoup, should be a soup object from request_articles_site

    will get all of the links by first getting the div they are in, and then all
    a with class = ""

    returns a list of links
    """

    div = soup.find("div", {"class" : "u-marginTop25"})

    return [a.get("href") for a in div.findAll("a", {"class" : ""})]

def download_website(link, date, driver):
    """
    params: link : string of url
            date : date so that we can find and/or create the file system.

    Goes to a specific url and saves the full html to a file in a folder system with dates

    the file system will be like this:
    tds_pages -> year -> month -> day -> files for this day

    will search the file system created with generate_file_structure to find
    which if a day/month/year is already present,

    This part uses selnium
    """
    path = pathlib.Path("tds_pages", str(date.year), str(date.month), str(date.day) )
    driver.get(link)

    time.sleep(2)

    html = driver.find_element_by_xpath("/html/body/div/div/article")

    article = html.get_attribute("innerHTML")
    soup = bs4.BeautifulSoup(article, "html.parser")

    title = soup.find("h1").text
    title = title.translate(str.maketrans("","", string.punctuation)).replace(" ", "_")

    file = open(pathlib.Path.joinpath(path, "{}.html".format(title)), "w+", encoding = "utf-8")
    #get the style
    #this is inefficient but I'm too tired to make it better right now
    full_html = driver.page_source
    full_soup = bs4.BeautifulSoup(full_html, "html.parser")

    head = full_soup.head

    file.write(str(head) + "\n" + str(soup))
    file.close()

def generate_file_structure(date_list):
    """
    params: date_list : list of datetime objects, should be created from get_sites()

    creates the data structure of empty folders and populates them with download_website
    """
    header = pathlib.Path("tds_pages")
    #check to see if the main folder exists
    if not os.path.isdir(header):
        os.makedirs(header)

    for date in date_list:
        year_folder = pathlib.Path.joinpath(header, str(date.year))
        if not os.path.isdir(year_folder):
            os.makedirs(year_folder)

        month_folder = pathlib.Path.joinpath(year_folder, str(date.month))
        if not os.path.isdir(month_folder):
            os.makedirs(month_folder)

        day_folder = pathlib.Path.joinpath(month_folder, str(date.day))
        if not os.path.isdir(day_folder):
            os.makedirs(day_folder)


def main():
    print("tds_scraper will download all html files of articles from towards data science")
    date_from = input("What time should its start?(day)-(month)-(year) ")
    date_to = input("What day should it end?(day)-(month)-(year)/(now) ")

    date_list = []
    print("Getting list of dates between {} and {}...".format(date_from, date_to))
    if date_to != "now":
        date_list = get_date_list(date_from, date_to)
    else:
        date_list = get_date_list(date_from)

    print("Generating file structure...")
    generate_file_structure(date_list)

    firefox_path = pathlib.Path("C:\\Users\\tuf90\\Desktop\\Python\\HelperDrivers\\geckodriver.exe")
    driver = webdriver.Firefox(executable_path = firefox_path)

    driver.get("https://towardsdatascience.com/")
    input("Use this time to login to your towardsdatascience account on the webdriver\n Press Enter when you've finished")


    print("Getting articles for requested dates...")
    for date in date_list:
        soup = request_articles_site(date)
        links = get_all_articles(soup)
        for link in links:
            download_website(link, date, driver)

    print("Finished getting all articles from {} to {}".format(date_from, date_to))
    print("Closing webdriver")
    driver.close()
    print("Finished!, enjoy your articles...")

if __name__ == "__main__":
    main()
