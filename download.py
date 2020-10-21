from get_stat import REGIONS, plot_stat 
import requests
import requests_cache
from bs4 import BeautifulSoup as bs, element
from re import compile
from os import mkdir, listdir, remove
import gzip
from  zipfile import ZipFile as zf
from io import TextIOWrapper
from csv import DictReader
import numpy as np

class YearStat:
    def __init__(self, region, crash_count, year):
        self.region = region
        self.crash_count = crash_count
        self.year = year


class DataDownloader():

    url = ""
    folder = ""
    cache_filename = ""
    cache = []

    def __init__(self, url="https://ehw.fit.vutbr.cz/izv/", folder="data", cache_filename="data_{}.pkl.gz"):
        self.url = url
        self.folder = folder
        self.cache_filename = cache_filename

    def get_links(self, response):
        soup = bs(response, "html.parser")
        data = soup.find_all("a", class_="btn-primary")
        return [entry["href"] for entry in data]

    def download_data(self):
        s = requests.session()
        header = {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Accept-Language": "cs-CZ,cs;q=0.9,ru;q=0.8",
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "DNT": "1",
                    "Host": "ehw.fit.vutbr.cz",
                    "Pragma": "no-cache",
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "cross-site",
                    "Sec-Fetch-User": "?1",
                    "Upgrade-Insecure-Requests": "1",
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36",}
        response = s.get(self.url, headers=header)
        links = self.get_links(response.text)

        # Create data containing folder
        if self.folder not in listdir():
            mkdir(self.folder)

        for link in links:
            file_name = link.split('/')[1]
            if file_name not in listdir(f"./{self.folder}"):
                # Download current file if it is not presents in archive folder
                try:
                    with open(f"./{self.folder}/{file_name}", "wb") as f:
                        with requests.get(f"{self.url}{link}", stream=True) as r:
                            for chunk in r.iter_content(chunk_size=128, decode_unicode=True):
                                f.write(chunk)
                except OSError:
                    # This can sometimes happen and error in SSL module for python > 3.7
                    pass
            
            with zf(f"{self.folder}/{file_name}", "r") as zip_ref:
                for file in zip_ref.namelist():
                    with zip_ref.open(file, "r") as zip_f:
                        lines = TextIOWrapper(zip_f, encoding = "ISO-8859-1")
                        with open(f"{self.folder}/{file}", "a+") as f:
                            for line in DictReader(lines):
                                f.write(";".join([ str(item) for item in line.values()]) + "\n")
            remove(f"{self.folder}/{file_name}")

    def parse_region_data(self, region) -> ([], np.array):
        for reg in region if region is not None else [REGIONS.keys()]:
            if REGIONS[reg][0] not in listdir(f"{self.folder}"):
                self.download_data()
            
        return ([], np.array)
        

    def get_list(self, regions = None):
        for region in regions if regions is not None else REGIONS.keys():
            if self.cache_filename.format(region) not in listdir(self.folder):
                pass

if __name__ == "__main__":
    requests_cache.install_cache('cache') 
    print("CACHE IS ON")
    DataDownloader().download_data()