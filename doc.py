import pandas as pd
import matplotlib.pyplot as plt
import contextily as ctx
import numpy as np
from scipy.stats import chi2_contingency



def make_df(df: pd.DataFrame) -> (pd.DataFrame, int):
    new = df[["p1", "p2b", "p13a", "p13b"]].copy()
    new.p2b = new.p2b.str.replace(
        r'(\d{2})(\d{2})', r'\1:\2', regex=True)
    new["p2b"] = pd.to_datetime(new["p2b"], format="%H:%M", errors="coerce")
    new = new.dropna()
    not_valid = len(df) - len(new)
    return (new, not_valid)


def make_predict(df: pd.DataFrame) -> bool:

    alpha = 0.05
    stat, p, dof, expected = chi2_contingency(df)
    print(stat, p, dof, expected)
    if p <= alpha:
        print("Accept our hipotez")
    else:
        print("Rejcet our hipotez")
    return False

def count_time(df: pd.DataFrame):
    df["result"] = df["p13a"] + df["p13b"]
    df["hard_res"] = df["result"] > 0
    df = df.resample("6H", on='p2b', offset="5H").agg({"p1": "count", "hard_res": "sum"}).reset_index()
    df["p2b"] = df["p2b"].dt.hour

    df = df.groupby("p2b").sum()
    df["p1"] = df.p1 - df.hard_res

    make_predict(df)

    return df.rename(columns={"p1": "not_hard_res"})

if __name__ == "__main__":
    df, not_valid = make_df(pd.read_pickle("accidents.pkl.gz"))
    new_df = count_time(df)
    # print(new_df)
