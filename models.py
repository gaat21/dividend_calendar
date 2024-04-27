from typing import Any
from dataclasses import dataclass

@dataclass
class StockData:
    id: str
    symbol: str
    slug: str
    exchange: str
    stock_name: str
    ex_date: str
    yield_percentage: float
    frequency: int
    amount: float
    previous_close_price: float
    high_price_52_week: float
    volume: int
    average_volume_20_day: int
    dividend_policy_status: str
    payable_date: str
    increase: str
    status: str
    qualification: str

    @staticmethod
    def from_dict(obj: Any) -> 'StockData':
        _id = str(obj.get("id"))
        _ex_date = str(obj.get("next_payout_ex_date"))
        _symbol = str(obj.get("symbol"))
        _slug = str(obj.get("slug"))
        _exchange = str(obj.get("exchange"))
        _stock_name = str(obj.get("stock_name"))
        _previous_close_price = float(obj.get("previous_close_price"))
        _high_price_52_week = float(obj.get("high_price_52_week"))
        _volume = int(obj.get("volume"))
        _average_volume_20_day = int(obj.get("average_volume_20_day"))
        _dividend_policy_status = str(obj.get("dividend_policy_status"))
        _frequency = int(obj.get("payout_frequency"))

        if not (obj.get("next_payout_amount") is None):
            _amount = float(obj.get("next_payout_amount"))
        else:
            _amount = -1.0
        
        _yield_percentage = ((_amount * _frequency) / _previous_close_price) * 100.0

        if obj.get("next_payout_ex_date") is None:
            _ex_date = "None"
        else:
            _ex_date = str(obj.get("next_payout_ex_date")).replace("T00:00:00.000+00:00", "")
        
        if obj.get("next_payout_payable_date") is None:
            _payable_date = "None"
        else:
            _payable_date = str(obj.get("next_payout_payable_date")).replace("T00:00:00.000+00:00", "")

        _increase = str(obj.get("next_payout_increase"))
        _status = str(obj.get("next_payout_status"))
        _qualification = str(obj.get("next_payout_qualification"))
        return StockData(_id, _symbol, _slug, _exchange, _stock_name, _ex_date, _yield_percentage, _frequency, _amount, _previous_close_price, _high_price_52_week, _volume, _average_volume_20_day, 
                         _dividend_policy_status, _payable_date, _increase, _status, _qualification)