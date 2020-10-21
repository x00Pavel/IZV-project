import get_stat

class DataDownloader():

    url = ""
    folder = ""
    cache_filename = ""

    def __init__(self, url=”https://ehw.fit.vutbr.cz/izv/”, folder=”data”, cache_filename=”data_{}.pkl.gz”):
        self.url = url
        self.folder = folder
        self.cache_filename = cache_filename

    def get_list(self, regions = None):
        pass

    def download_data(self):
        pass

    def parse_region_data(self, region):
        pass


if __name__ == "__main__":
    data = DataDownloader().get_list(["JHM"])