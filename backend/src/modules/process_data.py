import os
import sys
import pandas as pd
from datetime import datetime as dt
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.append(os.getcwd())
from src.modules import web_scraper as ws


data_path = os.path.join(os.getcwd(), "src", "data")
airport_data_filename = "Sydney_Airport_Tmax.csv"
airport_df = pd.read_csv(os.path.join(data_path, airport_data_filename))
months = [10, 11, 12]


def upsample_df(df):
    index = "DATE"
    df[index] = pd.to_datetime(df[index], format="mixed")
    df = df.loc[(df[index].dt.minute == 0) | (df[index].dt.minute == 30)].set_index(
        index
    )
    df_upsampled = (
        df.resample("5T").ffill().reset_index().rename(columns={"index": index})
    )
    return df_upsampled


def get_price_df(start_year):
    current_year = dt.now().year
    years = range(start_year, current_year)
    dfs = []

    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(ws.download_csv, year, month)
            for year in years
            for month in months
        ]
        dfs = [
            future.result()
            for future in as_completed(futures)
            if future.result() is not None
        ]

    price_df = pd.concat(dfs, ignore_index=True)

    price_df.rename(columns={"RRP": "PRICE", "SETTLEMENTDATE": "DATE"}, inplace=True)
    price_df.drop(columns=["PERIODTYPE", "REGION", "TOTALDEMAND"], inplace=True)

    return price_df


def get_q4_tmax_df(start_year):
    try:
        start_date = pd.to_datetime(f"1/1/{start_year}")
        airport_df = pd.read_csv(os.path.join(data_path, airport_data_filename))
        airport_df["Dates"] = pd.to_datetime(airport_df["Dates"])
        filtered_tmax = airport_df.loc[airport_df["Dates"] >= start_date]
        q4_tmax = filtered_tmax.loc[
            (filtered_tmax["Dates"].dt.month >= 10)
            & (filtered_tmax["Dates"].dt.month <= 12)
        ]
        q4_tmax.rename(columns={"Dates": "DATE"}, inplace=True)

        return upsample_df(q4_tmax)

    except Exception as e:
        print(e)


def get_scaled_prices(future_price, start_year):
    df = get_price_df(start_year)
    df["YEAR"] = df["DATE"].dt.year
    scaling_factors = future_price / df.groupby("YEAR")["PRICE"].mean()

    df["SCALED_PRICE"] = df["PRICE"] * df["YEAR"].map(scaling_factors).values

    return df


def get_daily_payout(df):
    df.index = pd.to_datetime(df.index)
    result_dict = {
        year: [[date.strftime("%m-%d"), round(payout, 2)] for date, payout in zip(group.index, group["Daily_Payout"])]
        for year, group in df.groupby(df.index.year)
    }
    return result_dict



def calculate_payout(strike, tmax_trigger, start_year):
    future_price = ws.get_future(timeout=20)

    with ThreadPoolExecutor() as executor:
        future_tmax_df = executor.submit(get_q4_tmax_df, start_year)
        future_scaled_price_df = executor.submit(
            get_scaled_prices, future_price, start_year
        )

    tmax_df = future_tmax_df.result()
    scaled_price_df = future_scaled_price_df.result()

    df = scaled_price_df.merge(tmax_df, on="DATE")

    payout_condition = df["Tmax"] >= tmax_trigger
    payout_values = (df["SCALED_PRICE"] - strike).clip(lower=0)
    df["Payout_5min"] = payout_values * payout_condition.astype(int)

    df["DATE"] = pd.to_datetime(df["DATE"])

    daily_df = (
        df.copy().groupby(df["DATE"].dt.date).agg({"Tmax": "max", "Payout_5min": "sum"})
    )
    daily_df.rename(columns={"Payout_5min": "Daily_Payout"}, inplace=True)

    annual_payout = df.groupby("YEAR")["Payout_5min"].sum().round(2)
    annual_payout_df = annual_payout.reset_index().rename(
        columns={"Payout_5min": "PAYOUT"}
    )

    daily_dict = get_daily_payout(daily_df)

    return annual_payout_df.to_dict(orient="list"), daily_dict
