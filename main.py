import requests
import pandas as pd
from tabulate import tabulate
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

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


def scrape_reviews_page(url, reviews):
    print("Scraping reviews list page...")
    soup2 = scrape_page(url)
    results2 = soup2.find(id="cm_cr-review_list")
    review_cards = results2.find_all("div", {'data-hook': 'review'})

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

        review = {'Name': name, 'Location': review_location, 'Occupation': occupation, 'Rating': rating,
                  'Title': review_title,
                  'Date': review_date,
                  'Body': review_body}

        reviews.append(review)
    return reviews


def main():
    try:
        print("Scraping product page for reviews list page...")
        url = "https://www.amazon.ca/dp/1789955750/ref=sspa_dk_detail_3?psc=1&pd_rd_i=1789955750&pd_rd_w=ysA69&content-id=amzn1.sym.c7dca932-da6a-44fc-af09-cc68d2449b34&pf_rd_p=c7dca932-da6a-44fc-af09-cc68d2449b34&pf_rd_r=BC37YMSSJZ77JTMS3HA3&pd_rd_wg=utjBQ&pd_rd_r=a58b079a-8110-4850-a1c3-c5da0ad68ba1&s=books&sp_csd=d2lkZ2V0TmFtZT1zcF9kZXRhaWw"
        soup = scrape_page(url)

        results = soup.find(id="cr-pagination-footer-0")
        link_url = results.find("a", class_="a-link-emphasis a-text-bold")['href']
        new_url = baseURL + link_url
    except:
        print("ERROR: User-Agent Expired, try another: https://developers.whatismybrowser.com/useragents/explore/")
        return 0

    print("Reviews list page found")
    reviews = []
    reviews = scrape_reviews_page(new_url, reviews)

    df = pd.DataFrame(reviews)
    print(tabulate(df, headers='keys', tablefmt='github'))


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
