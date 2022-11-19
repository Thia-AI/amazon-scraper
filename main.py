# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import requests
from bs4 import BeautifulSoup
from selenium import webdriver

baseURL = "https://www.amazon.ca"
headers = ({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36',
    'Accept-Language': 'en-US, en;q=0.5'});


def scrape_page(url):
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")
    return soup;

def scrape_rendered_page(url):
    diver = webdriver.Chrome()
    diver.get(url)
    html = diver.page_source
    # page = requests.get(url, headers=headers)
    soup = BeautifulSoup(html, "html.parser")
    return soup;

def main():
    try:
        url = "https://www.amazon.ca/Hands-Machine-Learning-Scikit-Learn-TensorFlow/dp/1492032646/ref=sr_1_3?crid=L76OSEZ3QFE8&keywords=machine+learning&qid=1668397114&qu=eyJxc2MiOiI1LjI1IiwicXNhIjoiNC43MiIsInFzcCI6IjQuNTEifQ%3D%3D&s=books&sprefix=machine+learning%2Cstripbooks%2C89&sr=1-3#customerReviews"
        soup = scrape_page(url)

        results = soup.find(id="cr-pagination-footer-0")
        link_url = results.find("a", class_="a-link-emphasis a-text-bold")['href']
        new_url = baseURL + link_url
    except:
        print("ERROR: User-Agent Expired, try another: https://developers.whatismybrowser.com/useragents/explore/")
        return 0

    soup2 = scrape_page(new_url)
    results2 = soup2.find(id="cm_cr-review_list")
    profiles = results2.find_all("a", class_='a-profile')

    for profile in profiles:
        print(profile['href'])

    profile_url = baseURL + profiles[0]['href']
    profile_soup = scrape_rendered_page(profile_url)
    profile_card = profile_soup.find(id="profile_v5")
    name = profile_card.find("span", class_="a-size-extra-large")
    print(name.text)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
