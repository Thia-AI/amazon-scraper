# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import requests
from bs4 import BeautifulSoup

baseURL = "https://www.amazon.ca"
headers = ({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
    'Accept-Language': 'en-US, en;q=0.5'});


def scrape_page(url):
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, "html.parser")
    return soup;


def main():
    URL = "https://www.amazon.ca/Hands-Machine-Learning-Scikit-Learn-TensorFlow/dp/1492032646/ref=sr_1_3?crid=L76OSEZ3QFE8&keywords=machine+learning&qid=1668397114&qu=eyJxc2MiOiI1LjI1IiwicXNhIjoiNC43MiIsInFzcCI6IjQuNTEifQ%3D%3D&s=books&sprefix=machine+learning%2Cstripbooks%2C89&sr=1-3#customerReviews"
    soup = scrape_page(URL)

    results = soup.find(id="cr-pagination-footer-0")
    link_url = results.find("a", class_="a-link-emphasis a-text-bold")['href']
    new_url = baseURL + link_url

    soup2 = scrape_page(new_url)
    results2 = soup2.find(id="cm_cr-review_list")
    profiles = results2.find_all("a", class_='a-profile')

    for profile in profiles:
        print(profile['href'])

    profile_url = baseURL + profiles[0]['href']
    profile_soup = scrape_page(profile_url)
    results3 = profile_soup.find(id="profile_v5")
    header = results3.find_all("div", class_="a-row a-spacing-none name-container")
    print(results3)
    print(header)
    # print(header)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
