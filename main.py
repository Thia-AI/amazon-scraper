import math
import os

import requests
import pandas as pd
from tabulate import tabulate
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

MAX_REVIEWS_PAGES_PER_PRODUCT = 10;

baseURL = "https://www.amazon.ca"
headers = ({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36',
    'Accept-Language': 'en-US, en;q=0.5'});


def scrape_page(url):
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")
    return soup;


def scrape_rendered_page(url):
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--incognito')
    options.add_argument('--headless')
    diver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    diver.get(url)
    # time.sleep(1)
    html = diver.page_source
    soup = BeautifulSoup(html, "html.parser")
    return soup;


def scrape_reviews(review_cards, reviews):
    for count, card in enumerate(review_cards, start=1):
        print("Scraping review ", count, "/", len(review_cards), "...")
        profile_link = card.find("a", class_='a-profile')
        a_row = card.find("div", class_="a-row")
        name = a_row.find("span", class_="a-profile-name").text.strip()
        rating = a_row.find("span", class_="a-icon-alt").text.split(" ")[0]
        review_title = a_row.find(attrs={'data-hook': 'review-title'}).find("span").text.strip()
        review_body = a_row.find("span", {'data-hook': 'review-body'}).find("span").text.strip()
        review_date_and_location = a_row.find("span", {'data-hook': 'review-date'}).text.strip()
        review_date = review_date_and_location.split(" on ")[1]
        review_location = review_date_and_location.split(" in ")[1].split(" on ")[0]
        occupation = ""

        if profile_link:
            print("Performing rendered profile scrape...")
            profile_url = baseURL + profile_link['href']
            profile_page = scrape_rendered_page(profile_url)
            profile_card = profile_page.find(id="profile_v5")
            name = profile_card.find("span", class_="a-size-extra-large").text.strip()
            occupation_and_location = profile_card.find("span", class_="a-size-base a-color-base")

            if (occupation_and_location):
                occupation = occupation_and_location.text.split(' | ')[0]
                review_location = occupation_and_location.text.split(' | ')[1]

        review = {'Name': name, 'Location': review_location, 'Rating': rating, 'Date': review_date,
                  'Occupation': occupation,
                  'Title': review_title,
                  'Body': review_body}

        reviews.append(review)
    return reviews


def main():
    try:
        url = "https://www.amazon.ca/dp/1789955750/ref=sspa_dk_detail_3?psc=1&pd_rd_i=1789955750&pd_rd_w=ysA69&content-id=amzn1.sym.c7dca932-da6a-44fc-af09-cc68d2449b34&pf_rd_p=c7dca932-da6a-44fc-af09-cc68d2449b34&pf_rd_r=BC37YMSSJZ77JTMS3HA3&pd_rd_wg=utjBQ&pd_rd_r=a58b079a-8110-4850-a1c3-c5da0ad68ba1&s=books&sp_csd=d2lkZ2V0TmFtZT1zcF9kZXRhaWw"
        print("Scraping product page for reviews list page...  ", url)
        soup = scrape_page(url)

        results = soup.find(id="cr-pagination-footer-0")
        print("Reviews list page found")

        link_url = results.find("a", class_="a-link-emphasis a-text-bold")['href']
        new_url = baseURL + link_url
    except:
        print("ERROR: User-Agent Expired, try another: https://developers.whatismybrowser.com/useragents/explore/")
        return 0

    print("Scraping reviews list page...")
    soup2 = scrape_page(new_url)

    # find number of pages to scrape in reviews list, maximum 10 pages (100 reviews)
    total_num_reviews = \
        soup2.find("div", {'data-hook': 'cr-filter-info-review-rating-count'}).text.split(', ')[1].split(" ")[0]
    total_num_reviews = int(total_num_reviews)
    number_of_review_pages_to_scrape = math.ceil(
        total_num_reviews / MAX_REVIEWS_PAGES_PER_PRODUCT) if total_num_reviews < MAX_REVIEWS_PAGES_PER_PRODUCT * 10 else 10

    # go through the review pages and scrape the review data
    reviews = []
    for page_number in range(1, number_of_review_pages_to_scrape + 1):
        pageUrl = new_url + '&pageNumber=' + str(page_number)
        print("Scaping page number ", page_number, "...   ", pageUrl)
        soup3 = scrape_page(pageUrl)
        review_list = soup3.find(id="cm_cr-review_list")
        review_cards = review_list.find_all("div", {'data-hook': 'review'})
        reviews = scrape_reviews(review_cards, reviews)

    print("Scraping Finished, converting data into cool tabular view...")
    df = pd.DataFrame(reviews)
    print(tabulate(df, headers='keys', tablefmt='github'))
    os.makedirs('csv', exist_ok=True)
    df.to_csv('csv/out.csv', index=False)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
