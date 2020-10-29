import requests
import requests_cache
from bs4 import BeautifulSoup as bs, element
from re import compile
from os import mkdir, listdir, remove
from  zipfile import ZipFile as zf
from io import TextIOWrapper
from csv import DictReader
import numpy as np
from glob import glob
from pprint import pprint as pp
import pickle
import time

REGIONS ={
    "PHA": ("00.csv", "Hlavní město Praha"),
    "STC": ("01.csv", "Středočeský"),
    "JHC": ("02.csv", "Jihočeský"),
    "PLK": ("03.csv", "Plzeňský"),
    "KVK": ("19.csv", "Karlovarský"), 
    "ULK": ("04.csv", "Ústecký"),
    "LBK": ("18.csv", "Liberecký"),
    "HKK": ("05.csv", "Královéhradecký"), 
    "PAK": ("17.csv", "Pardubický"),
    "OLK": ("14.csv", "Olomoucký"),
    "MSK": ("07.csv", "Moravskoslezský"), 
    "JHM": ("06.csv", "Jihomoravský"),
    "ZLK": ("15.csv", "Zlínský"),
    "VYS": ("16.csv", "Kraj Vysočina") 
}


class DataDownloader():
    """Class for downloading and preprocessing data."""
    url = ""
    folder = ""
    cache_filename = ""
    output = None
    cache = {}
    columns = ["REGION", "DRUH POZEMNÍ KOMUNIKACE", "ČÍSLO POZEMNÍ KOMUNIKACE", "den, měsíc, rok", "DEN V TYDNU", "CAS", 
               "DRUH NEHODY", "DRUH SRÁŽKY JEDOUCÍCH VOZIDEL", "DRUH PEVNÉ PŘEKÁŽKY", "CHARAKTER NEHODY", "ZAVINĚNÍ NEHODY", 
               "ALKOHOL U VINÍKA NEHODY PŘÍTOMEN", "HLAVNÍ PŘÍČINY NEHODY", "usmrceno osob", "těžce zraněno osob", "lehce zraněno osob", 
               "CELKOVÁ HMOTNÁ ŠKODA", "DRUH POVRCHU VOZOVKY", "STAV POVRCHU VOZOVKY V DOBĚ NEHODY", "STAV KOMUNIKACE", 
               "POVĚTRNOSTNÍ PODMÍNKY V DOBĚ NEHODY", "VIDITELNOST", "ROZHLEDOVÉ POMĚRY", "DĚLENÍ KOMUNIKACE", 
               "SITUOVÁNÍ NEHODY NA KOMUNIKACI", "ŘÍZENÍ PROVOZU V DOBĚ NEHODY", "MÍSTNÍ ÚPRAVA PŘEDNOSTI V JÍZDĚ", 
               "SPECIFICKÁ MÍSTA A OBJEKTY V MÍSTĚ NEHODY", "SMĚROVÉ POMĚRY", "POČET ZÚČASTNĚNÝCH VOZIDEL", "MÍSTO DOPRAVNÍ NEHODY", 
               "DRUH KŘIŽUJÍCÍ KOMUNIKACE", "DRUH VOZIDLA", "VÝROBNÍ ZNAČKA MOTOROVÉHO VOZIDLA", "ROK VÝROBY VOZIDLA", 
               "CHARAKTERISTIKA VOZIDLA", "SMYK", "VOZIDLO PO NEHODĚ", "ÚNIK PROVOZNÍCH, PŘEPRAVOVANÝCH HMOT", 
               "ZPŮSOB VYPROŠTĚNÍ OSOB Z VOZIDLA", "SMĚR JÍZDY NEBO POSTAVENÍ VOZIDLA", "ŠKODA NA VOZIDLE", "KATEGORIE ŘIDIČE", 
               "STAV ŘIDIČE", "VNĚJŠÍ OVLIVNĚNÍ ŘIDIČE", "<a>", "<b>", "<c>", "SOURADNICE X", "SOURADNICE Y", 
               "<f>","<g>","<h>","<i>","<j>","<k>","<l>","<o>","<p>","<q>","<r>","<s>","<t>","LOKALITA NEHODY"]
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
        """Initialise object of given class and creates folder for storing data.
        
        Keyarguments:
        url -- base url to download data (default https://ehw.fit.vutbr.cz/izv/)
        folder -- directory, where downloaded and processed data should be 
                  stored (default data)
        cache_filename -- filename for storing already processed data (default 
                          data_{}.pkl.gz). Should contain placeholder for region code
        """
        self.url = url
        self.folder = folder
        self.cache_filename = cache_filename
        if self.folder not in listdir():
            mkdir(self.folder)

    def get_links(self, response):
        """Parse HTML response and extract all links to .zip files.
        
        Arguments:
        response -- HTML response from request on self.url

        Return:
        list of relative paths to archives
        """
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
    
    def download_data(self, regions = None):
        """Donwload, filter and preprocess data from self.url.
        
        Store processed data in program cache.

        Arguments:
        regions -- list of regions to extract and preprocess (default None)
        """
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


        for link in links:
            archive_name = link.split('/')[1]
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

        archives = glob(f"{self.folder}/*zip")
        if not regions:
            regions = self.file_to_reg.values()
        else:
            regions = [REGIONS[reg][0] for reg in regions]
        result = None
        # Read data from CSV files to program memory
        for archive in archives:
            print(f"Archive is open: {archive}")
            zip_archive = zf(archive)
            for file in zip_archive.namelist():
                if file in regions:
                    print(f"File is open: {file}")
                    region = self.file_to_reg[file]
                    values = np.genfromtxt(zip_archive.open(file), delimiter=";", 
                                                    encoding="ISO-8859-1", 
                                                    dtype="unicode", 
                                                    autostrip=True,
                                                    missing_values="XX",
                                                    filling_values="-1",
                                                    usecols=(np.arange(1,64)),
                                                    )
                    if result is None:
                        result = np.insert(values, 0, region, axis=1)
                    else:
                        result = np.concatenate((result, np.insert(values, 0, region, axis=1)))
        
        print("Start processing dataset")
        result = list(np.transpose(result))
        letters = ['A:', 'B:', 'D:', 'E:', 'F:', 'G:', 'H:', 'J:']
        # Filter data, deleting wrong formated ciles
        for index, arr in enumerate(result):
            for index_inner, elem in enumerate(arr):
                tmp = [ext for ext in letters if ext in elem]
                if tmp != []:
                    for letter in tmp:
                        elem = elem.replace(letter, '')
                if elem == '""':
                    elem = "-1"
                if ',' in elem:
                    elem = elem.replace(',', '.')
                if '"' in elem:
                    elem = elem.replace('"', '')
                if elem == '':
                    elem = "-1"
                arr[index_inner] = elem

            result[index] = arr        


        result[0]  = result[0].astype(np.unicode)
        result[1]  = result[1].astype(np.int8)
        result[2]  = result[2].astype(np.int8)
        result[3]  = result[3].astype(np.datetime64)
        result[4]  = result[4].astype(np.int8)
        result[5]  = result[5].astype(np.unicode)
        result[6]  = result[6].astype(np.int8)
        result[7]  = result[7].astype(np.int8)
        result[8]  = result[8].astype(np.int8)
        result[9]  = result[9].astype(np.int8)
        result[10] = result[10].astype(np.int8)
        result[11] = result[11].astype(np.int8)
        result[12] = result[12].astype(np.int16)
        result[13] = result[13].astype(np.int8)
        result[14] = result[14].astype(np.int8)
        result[15] = result[15].astype(np.int8)
        result[16] = result[16].astype(np.int16)
        result[17] = result[17].astype(np.int8)
        result[18] = result[18].astype(np.int8)
        result[19] = result[19].astype(np.unicode)
        result[20] = result[20].astype(np.int8)
        result[21] = result[21].astype(np.int8)
        result[22] = result[22].astype(np.int8)
        result[23] = result[23].astype(np.int8)
        result[24] = result[24].astype(np.int8)
        result[25] = result[25].astype(np.int8)
        result[26] = result[26].astype(np.int8)
        result[27] = result[27].astype(np.unicode)
        result[28] = result[28].astype(np.int8)
        result[29] = result[29].astype(np.int8)
        result[30] = result[30].astype(np.int8)
        result[31] = result[31].astype(np.int8)
        result[32] = result[32].astype(np.int8)
        result[33] = result[33].astype(np.int8)
        result[34] = result[34].astype(np.unicode)
        result[35] = result[35].astype(np.int8)
        result[36] = result[36].astype(np.bool)
        result[37] = result[37].astype(np.int8)
        result[38] = result[38].astype(np.int8)
        result[39] = result[39].astype(np.int8)
        result[40] = result[40].astype(np.int8)
        result[41] = result[41].astype(np.int16)
        result[42] = result[42].astype(np.int8)
        result[43] = result[43].astype(np.int8)
        result[44] = result[44].astype(np.int8)
        result[45] = result[45].astype(np.float)
        result[46] = result[46].astype(np.float)
        result[47] = result[47].astype(np.float)
        result[48] = result[48].astype(np.float)
        result[49] = result[49].astype(np.float)
        result[50] = result[50].astype(np.float)
        result[51] = result[51].astype(np.unicode)
        result[52] = result[52].astype(np.unicode)
        result[53] = result[53].astype(np.unicode)
        result[54] = result[54].astype(np.unicode)
        result[55] = result[55].astype(np.unicode)
        result[56] = result[56].astype(np.unicode)
        result[57] = result[57].astype(np.float)
        result[58] = result[58].astype(np.unicode)
        result[59] = result[59].astype(np.unicode)
        result[60] = result[60].astype(np.unicode)
        result[61] = result[61].astype(np.unicode)
        result[62] = result[62].astype(np.unicode)
        result[63] = result[63].astype(np.unicode)

        # Creating program cache
        if self.output is None:
            self.output = result
        else:
            for index in range(0, len(self.output)):
                self.output[index] = np.concatenate(
                    (self.output[index], result[index]))
        print("Dataset processing finished")

    def parse_region_data(self, region="PHA") -> ([str], [np.array]):
        """"Parse data for given region.
        
        Arguments:
        region -- three-letter code of region that should be parsed (default PHA)

        Return:
        tuple of two lists. First list contain names for each column in second 
        list with numpy.array lists inside.
        """
        if self.folder not in listdir():
            mkdir(self.folder)
        if self.cache_filename.format(region) not in listdir(self.folder):
            self.download_data([region])

        
        indexes = np.where(self.output[0] == region)
        a = [np.take(self.output[i], indexes)[0] for i in range(len(self.output))]
        return (self.columns, a)
        

    def get_list(self, regions = None) -> ([str], [np.array]):
        """Get data set for given regions.

        Data for each region would be parsed using parse_region_data(region)
        method. If cache file for current regions is present in data folder,
        that data would be loaded from this file. If data already stored in 
        program cache, they also will be loaded from cache and stored to cache file
        without calling parse_region_data(region) metod.

        Arguments:
        regions -- list of three-letter regions code that should presents in 
                   output (default None, thath means all regions)

        Return:
        tuple of two lists. First list contain names for each column in second
        list with numpy.array lists inside. Second list contain data for each
        regions from regions argument.        
        """
        res_columns = []
        values = []
        stats = None
        for region in regions if regions is not None else REGIONS.keys():
            if region in self.cache.keys():
                stats = self.cache[region]
                print("Data in program cache")
            elif self.cache_filename.format(region) in listdir(self.folder):
                with open(f'{self.folder}/{self.cache_filename.format(region)}','rb') as f:
                    stats = pickle.load(f)
                print('Data in cache files')
            else:
                stats = self.parse_region_data(region)
                with open(f"{self.folder}/{self.cache_filename.format(region)}",'wb') as f:
                    pickle.dump(stats, f)
                self.cache[region] = stats
            
            res_columns = stats[0]
            tmp = stats[1]
            if values == []:
                values = tmp
            else:
                for i in range(0,45):
                    values[i] = np.concatenate((values[i], tmp[i])) 
                
        return (res_columns, values)


if __name__ == "__main__":
    requests_cache.install_cache('cache') 
    print("CACHE IS ON")
    star_s= time.time()
    columns, values = DataDownloader().get_list()
    print(f"{'#'*80}\nTotal time: {time.time() - star_s}\n{'#'*80}")
    res_str = "\n".join([f"{columns[i]} -> {values[i]}" for i in range(0, len(columns))])
    print(f"Column names:\n{res_str}")
    print("#"*80)
    print(f"{' '*25}Count of crashes: {values[0].size}")
    print("#"*80)
