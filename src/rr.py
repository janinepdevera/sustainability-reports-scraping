"""
A scraper for Responsibility Reports Library (https://www.responsibilityreports.com/).
"""

# standard library
import re
import datetime
import os

# web services
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService 
from webdriver_manager.chrome import ChromeDriverManager 
from tqdm import tqdm
from urllib.parse import urljoin

class ReportsScraper():
    def __init__(self):
        self.base = 'https://www.responsibilityreports.com/'
        self.main = f'{self.base}Companies?a='
        self.mainsoup = None
        self.urlsoup = None

    def parse_main(self, input_page=None):
        input_page = input('Input company:')
        
        options = webdriver.ChromeOptions()
        options.add_argument('--headless') 
        
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        #driver.get(self.main)
        driver.get(f'{self.main}{input_page}')
        self.mainsoup = BeautifulSoup(driver.page_source, 'html.parser')
        driver.quit()

        return self.mainsoup
    
    def _get_links(self, class_name: str, soup):
        urls = []
        for link in soup.find_all(class_=class_name):
            try:
                a_tag = link.find('a')
                href_tag = a_tag.attrs['href']
                url = urljoin(self.base, href_tag)
                urls.append(url)

            except Exception as e:
                print("An exception occurred:", e)

        return urls
    
    def get_company_links(self):
        company_links = self._get_links('companyName', self.mainsoup)
        return company_links
    
    def parse_companies(self, link):
        r = requests.get(link)
        self.urlsoup = BeautifulSoup(r.content, features="html.parser")
        return self.urlsoup
    
    def get_report_links(self):
        report_links = self._get_links('btn_archived download', self.urlsoup)
        return report_links
    
    def download_reports(self):
        company_links = self.get_company_links()
        os.makedirs("./reports/", exist_ok=True)

        for link in company_links:
            urlsoup = self.parse_companies(link)
            company = urlsoup.find_all(class_='heading')[0]
            company_name = re.sub(r'\W+', '', company.text)

            reports = urlsoup.find_all(class_="heading")
            report_links = self.get_report_links()

            i = 0
            for report in report_links: 
                i += 1
                report_name = reports[i].text
                report_name = re.sub(r'\W+', '', report_name)
                filename = f'./reports/{company_name}_{report_name}.pdf'

                if not os.path.exists(filename):
                    r = requests.get(report)
                    with open(filename, 'wb') as pdf:
                        pdf.write(r.content) 
                        print(f'File {company_name}_{report_name} downloaded.')

scraper = ReportsScraper()
scraper.parse_main()
scraper.download_reports()