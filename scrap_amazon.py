import requests
from bs4 import BeautifulSoup
import mysql.connector as db


class amazon():
    def __init__(self, zipcode):
        self.config = {
            "host": "localhost",
            "user": "root",
            "password": '',
            "database": "amazon_db"
        }
        self.ss = requests.Session()
        self.zipcode = zipcode
        self.prx = {
            "http": "http://127.0.0.1:8888",
            "https": "https://127.0.0.1:8888"
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        open_amazon = self.ss.get(
            'https://www.amazon.in/', headers=headers, verify=False, proxies=self.prx)
        headers2 = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0',
            'Accept': 'text/html,*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded',
            'anti-csrftoken-a2z': 'gB1tL8U9DK6Wroi1NDg1Ahjxe4oYN54pb+Ja0DsAAAAMAAAAAGCCvJRyYXcAAAAA',
            'contentType': 'application/x-www-form-urlencoded;charset=utf-8',
            'Content-Length': '129',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Referer': 'https://www.amazon.in/'

        }
        data = {
            'locationType': 'LOCATION_INPUT',
            'zipCode': self.zipcode,
            'storeContext': 'hpc',
            'deviceType': 'web',
            'pageType': 'Detail',
            'actionSource': 'glow',
            'almBrandId': 'undefined'
        }
        change_zip = self.ss.post(
            'https://www.amazon.in/gp/delivery/ajax/address-change.html', headers=headers2, verify=False, proxies=self.prx, data=data)

    def fetch_data(self):
        conn = db.connect(**self.config)
        conn.autocommit = True
        mycursor = conn.cursor(dictionary=True)
        mycursor.execute("select * from url")
        data = mycursor.fetchall()
        mycursor.close()
        conn.close()
        return data

    def scrap_data(self, data):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        store_data_list = []
        for dat in data:
            open_amazon = self.ss.get(
                dat['url'], headers=headers, verify=False, proxies=self.prx)
            soup = BeautifulSoup(open_amazon.text, 'html.parser')
            asin = dat['url'].split('/')[-1]
            title = soup.find(
                'span', {'id': 'productTitle'}).text.replace('\n', '')
            brand = soup.find('a', {'id': 'bylineInfo'}).text.replace('\n', '')

            price = soup.find('span', {'id': 'priceblock_ourprice'}).text.replace(
                '\n', '').replace('\xa0', '') if soup.find('span', {'id': 'priceblock_ourprice'}) != None else ''
            sold_by = soup.find(
                'a', {'id': 'sellerProfileTriggerId'}).text.replace('\n', '') if soup.find('a', {'id': 'sellerProfileTriggerId'}) != None else ''

            store_data_list.append(
                (dat['id'], asin, title, brand, price, sold_by))
        return store_data_list

    def store_data(self, data):
        conn = db.connect(**self.config)
        conn.autocommit = True
        mycursor = conn.cursor()
        mycursor.executemany(
            "insert into product_details (url_id,asin,title,brand,price,sold_by) values (%s,%s,%s,%s,%s,%s)", data)
        conn.commit()
        mycursor.close()
        conn.close()


if __name__ == "__main__":
    t = amazon('122001')
    data = t.fetch_data()
    scrap = t.scrap_data(data)
    t.store_data(scrap)
