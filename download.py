from get_stat import REGIONS, plot_stat 
import requests
import requests_cache
from bs4 import BeautifulSoup as bs, element
from re import compile, findall
from os import mkdir, listdir, remove
import gzip
from  zipfile import ZipFile as zf
from io import TextIOWrapper
from csv import DictReader, reader
import pickle
import numpy as np

class Crash:
    def __init__(self, row=None, region=None, **kwargs):
        self.region = region
        if row: 
            dat_split = row[3].split("-")
            self.year = np.uint16(dat_split[0])
            self.month = np.int8(dat_split[1])
            self.day = np.int8(dat_split[2])
            self.week_day = np.int8(row[4])
            self.hours = np.int8(row[5][0:2:]) if np.int8(row[5][0:2:]) < 25 else -1
            self.minutes = np.int8(row[5][2:5]) if np.int8(row[5][2:5:]) < 60 else -1
            self.road_type = row[1]
            self.road_number = row[2]
            self.crash_type = row[6]
        

class DataDownloader():

    url = ""
    folder = ""
    cache_filename = ""
    cache = {}
    # crash_dtype = np.dtype([("region", np.unicode_, 3),("year",np.uint16,1), ("month",np.uint8,1), ("day",np.uint8,1), ("hours",np.int8,1), ("minutes",np.int8,1)])
    file_to_reg = {
        "00.csv": "PHA",
        "01.csv": "STC",
        "02.csv": "JHC",
        "03.csv": "PLK",
        "19.csv": "KVK",
        "04.csv": "ULK",
        "18.csv": "LBK",
        "05.csv": "HKK",
        "17.csv": "PAK",
        "14.csv": "OLK",
        "07.csv": "MSK",
        "06.csv": "JHM",
        "15.csv": "ZLK",
        "16.csv": "VYS",
        # "CHODCI.csv": "CHODCI"
    }

    def __init__(self, url="https://ehw.fit.vutbr.cz/izv/", folder="data", cache_filename="data_{}.pkl.gz"):
        self.url = url
        self.folder = folder
        self.cache_filename = cache_filename

    def get_links(self, response):
        soup = bs(response, "html.parser")
        data = soup.find_all("td", class_="text-center", text=compile(r"Prosinec \d{4}"))
        links = []
        for entry in data:
            tr = entry.parent
            # Find last link for each year
            while True:
                try:
                    a = tr.findChildren("a", class_="btn-primary")[0]
                    links.append(a["href"])
                    break
                except IndexError:
                    tr = tr.previous_sibling
                    continue
        return links

    def download_data(self, region=None):
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
        if self.folder not in listdir("./"):
            mkdir(self.folder)

        for link in links:
            archive_name = link.split('/')[1]
            # year = findall(r"([0-9]{4})\.zip$", archive_name)[0]

            if archive_name not in listdir(f"./{self.folder}"):
                # Download current file if it is not presents in archive folder
                try:
                    with open(f"./{self.folder}/{archive_name}", "wb") as f:
                        with requests.get(f"{self.url}{link}", stream=True) as r:
                            for chunk in r.iter_content(chunk_size=128, decode_unicode=True):
                                f.write(chunk)
                except OSError:
                    # This can sometimes happen and error in SSL module for python > 3.7
                    pass
            archive = zf(f"{self.folder}/{archive_name}")
            # with zf(f"{self.folder}/{archive_name}", "r") as archive:
            
            for file in archive.namelist():
                if file in self.file_to_reg.keys():
                    reg = self.file_to_reg[file]
                    if reg not in self.cache.keys():
                        self.cache[reg] = np.genfromtxt(archive.open(file), 
                                                        delimiter=";", 
                                                        encoding="ISO-8859-1", 
                                                        dtype="unicode", 
                                                        autostrip=True, 
                                                        usecols=(0,1,2,3))
                    else:
                        np.concatenate([self.cache[reg], np.genfromtxt(archive.open(file), 
                                                                       delimiter=";", 
                                                                       encoding="ISO-8859-1", 
                                                                       dtype="unicode", 
                                                                       autostrip=True, 
                                                                       usecols=(0,1,2,3))])
        for reg, values in self.cache.items():
            self.cache[reg] = np.transpose(values)
            self.cache[reg][0] = self.cache[reg][0].astype("unicode")
        # print(self.cache["HKK"])
        print(self.cache["HKK"][0])
            #     with archive.open(file, "r") as zip_f:
            #             lines = TextIOWrapper(zip_f, encoding = "ISO-8859-1")
            #             try:
            #                 with open(f"{self.folder}/{self.file_to_reg[file]}.csv", "a+") as f:
            #                     for line in DictReader(lines):
            #                         f.write(";".join([ str(item) for item in line.values()]) + "\n")
            #             except KeyError:
            #                 continue
            # remove(f"{self.folder}/{archive_name}")

    def parse_region_data(self, region) -> ([], np.ndarray):
        columns = ["region", "year", "month", "day", "hours", "minutes"]
        if self.folder not in listdir():
            self.download_data()
            
        values = None
        # with open(f"{self.folder}/{region}.csv", "r") as f:
        #     csv_file = reader(f, delimiter=";")
        #     crashes = [Crash(row, region) for row in csv_file]
        #     reg_int = REGIONS[region][0]
        #     values = np.array([[reg_int, 
        #                         crash.year, crash.month, crash.day,
        #                         crash.hours, crash.minutes] for crash in crashes])

        return (columns, values)
        

    def get_list(self, regions = ["HKK"]):
        columns = ["region", "year", "month", "day", "hours", "minutes"]
        empty = []
        if self.folder not in listdir("./"):
            self.download_data()
        
        for region in regions if regions is not None else REGIONS.keys():
            if region in self.cache.keys():
                empty.append(self.cache[region][1])
            elif self.cache_filename.format(region) in listdir(self.folder):
                with open(f"{self.folder}/{self.cache_filename.format(region)}", "rb") as f:
                    empty.append(pickle.load(f))
            else:
                columns, values = self.parse_region_data(region)
                self.cache[region] = (columns, values)
                with open(f"{self.folder}/{self.cache_filename.format(region)}", "wb") as f:
                    pickle.dump(values, f)
                empty.append(values)
        res = np.concatenate(empty)
        return (columns, np.transpose(res))
             
if __name__ == "__main__":
    requests_cache.install_cache('cache') 
    print("CACHE IS ON")
    DataDownloader().download_data()
    # regions = ["HKK", "JHC", "LBK"]
    # data = DataDownloader().get_list(regions)
    # print(data[1])
    # print(f"Regions: {', '.join(regions)}\nColumns: {', '.join(data[0])}\nSize of dataset: {data[1].size}")
    # plot_stat(data)