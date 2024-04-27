import json
import sys
from typing import List
import pandas
import requests

from bs4 import BeautifulSoup
from models import StockData
import os

url = "https://www.dividend.com/api/t2/body.html" #"https://www.dividend.com/monthly-income-from-monthly-dividend-stocks-etfs-and-funds/"

def main() -> None:
    print("Start collect next month dividends.")

    df = pandas.DataFrame()
    if os.path.exists("dividend.xlsx"):
        print("Loading dividend.xlsx")
        df = pandas.read_excel("dividend.xlsx", sheet_name="Stocks")
        for _, row in df.iterrows():
            print(f"Loaded stock: {row['stock_name']} - {row['symbol']} - {row['ex_date']}")

    print("Collecting new dividend stocks")
    dividend_stocks = get_dividend_stocks()
    print(f"Get dividend stocks count: {len(dividend_stocks)}")
    new_df = pandas.DataFrame(dividend_stocks)
    # Filter out OTC stocks and None ex_date
    new_df = new_df[new_df["exchange"] != "OTC"]
    new_df = new_df[new_df["ex_date"] != "None"]

    # Check dividend stocks already exists
    if len(df) > 0:
        for index, new_row in new_df.iterrows():
            if any(df["id"] == new_row["id"]) and any(df["ex_date"] == new_row["ex_date"]):
                print(f"Stock {new_row['symbol']} already exists")
                new_df = new_df.drop(index)
            else:
                print(f"New stock: {new_row['stock_name']} - {new_row['symbol']} - {new_row['ex_date']}")
    
    print(f"New dividend stocks count: {len(new_df)}")
    if len(new_df) > 0:
        pandas.concat([df, new_df]).to_excel(f"dividend.xlsx", sheet_name="Stocks", index=False, )

def get_dividend_stocks() -> List[StockData]:
    payload = json.dumps({
        "uuid": "Merged-SEOTable",
        "default_filters": [
            {
                "filterKey": "ShareClass",
                "value": [
                    "Commons"
                ],
                "filterType": "FilterShareClass",
                "filterCollection": [
                    "CollectionMergedStocks"
                ],
                "esType": "keyword"
            }
        ],
        "filters": {
            "FilterShareClass": {
                "filterKey": "FilterShareClass",
                "selected": "true",
                "value": [
                    "Commons"
                ],
                "type": ""
            },
            "FiilterDividendYieldCurrent_from": {
                "filterKey": "FiilterDividendYieldCurrent_from",
                "selected": "true",
                "value": 8,
                "type": "decimal"
            },
             "FilterPayoutFrequency": {
                "filterKey": "FilterPayoutFrequency",
                "selected": "true",
                "value": [
                    "12"
                ],
                "type": ""
            }
        },
        "page": 1,
        "collection": "CollectionMergedStocks",
        "sort_by": {
            "PayoutNextExDate": "asc"
        },
        "theme": "FIN::L3(Monthly Div Freq)",
        "ad_unit_full_path": "/2143012/Div/Theme/IncMonthly"
    })

    resp = requests.post(url, data=payload, headers={
        "Content-Type": "application/json",
        "Host": "www.dividend.com"
    })
    resp.raise_for_status()

    if resp.status_code != 200:
        print(f"Request failed with status code: {resp.status_code}")
        return
    
    soup = BeautifulSoup(resp.content, "html.parser")
    table_rows = soup.find_all("div", {"class": "mp-table-body-row-container mp-table-row t-static"})
    stocks = []
    for row in table_rows:        
        stock_name = row.find("div", {"class": "mp-table-body-cell__sticky"}).find("a").text
        stock_symbol = row.find("div", {"class": "mp-table-body-cell__sticky"}).find("span").text
        detail_link = row.find("div", {"class": "mp-table-body-cell__sticky"}).find("a")["href"]
        slug_name = detail_link[:-1].split("/")[-1]
        print(f"Stock: {stock_name} - {stock_symbol} - {slug_name}")
        stocks.append(get_stock_data(slug_name))
    
    return stocks
       
def get_stock_data(slug_name: str) -> StockData:
    stock_url = "https://www.dividend.com/api/dividend/stocks/"
    payload = json.dumps({
        "slug": f"{slug_name}",
        "columns": [
            "id",
            "symbol",
            "slug",
            "exchange",
            "stock_name",
            "market_cap_size",
            "sector",
            "industry",
            "subindustry",
            "security_category",
            "dars_overall_notes",
            "previous_close_price",
            "low_price_52_week",
            "high_price_52_week",
            "latest_yield",
            "market_cap",
            "average_days_to_recovery",
            "yield_on_cost",
            "volume",
            "average_volume_20_day", 
            "dividend_policy_status",
            "next_payout_amount",
            "next_payout_ex_date",
            "next_payout_payable_date",
            "next_payout_type",
            "next_payout_increase",
            "next_payout_status",
            "next_payout_qualification",
            "payout_frequency"
        ]
    })
    resp = requests.post(stock_url, data=payload, headers={"Content-Type": "application/json"})
    resp.raise_for_status()

    ignored_values = ['null', '', None, False, 'false', 'N/A']
    json_data = resp.json()
    result = {}
    for key in json_data.keys():
        if json_data[key] not in ignored_values:
            result.update({key: json_data[key]})

    return StockData.from_dict(result)

if __name__ == "__main__":
    sys.exit(main())