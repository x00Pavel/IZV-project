REGIONS={
    "PHA": (0, "Hlavní město Praha"),
    "STC": (1, "Středočeský"),
    "JHC": (2, "Jihočeský"),
    "PLK": (3, "Plzeňský"),
    "KVK": (19, "Karlovarský"), 
    "ULK": (4, "Ústecký"),
    "LBK": (18, "Liberecký"),
    "HKK": (5, "Královéhradecký"), 
    "PAK": (17, "Pardubický"),
    "OLK": (14, "Olomoucký"),
    "MSK": (7, "Moravskoslezský"), 
    "JHM": (6, "Jihomoravský"),
    "ZLK": (15, "Zlínský"),
    "VYS": (16, "Kraj Vysočina"),
    0: "PHA",
    1: "STC",
    2: "JHC",
    3: "PLK",
    19: "KVK",
    4: "ULK",
    18: "LBK",
    5: "HKK",
    17: "PAK",
    14: "OLK",
    7: "MSK",
    6: "JHM",
    15: "ZLK",
    16 : "VYS",
}

def plot_stat(data_source, fig_location = None, show_figure = False):
    columns, values = data_source
    res = {}
    for region, year, *_ in values:
        if region not in res.keys():
            res[region] = {}
        else:
            if year not in res[region].keys():
                res[region][year] = 1
            else:
                res[region][year] += 1
    for reg, stats in res.items():
        vals = '\n\t'.join([f'{year} -> {count}' for year, count in stats.items()])
        print(f"Region: {REGIONS[reg]} - {REGIONS[REGIONS[reg]][1]}\n\t{vals}")
    # print(columns)
    