from pandas import DataFrame

from models.dto.candle_request_dto import CandleRequestDto
from models.entity.candle_data import CandleData
from models.dto.candle_response_dto import CandleResponseDto
from models.type.ema import EMA
from models.type.macd import MACD
from module.upbit_module import UpbitModule
from repository.candle_data_repository import CandleDataRepository


class CandleService:
    def __init__(self,
                 ema: EMA,
                 upbit_module: UpbitModule,
                 candle_data_repository: CandleDataRepository):
        self.candle_data_repository = candle_data_repository
        self.ema = ema
        self.upbit_module = upbit_module

    def create_sub_data(self, data: DataFrame):
        data[EMA.SHORT] = data[CandleResponseDto.CLOSE].ewm(span=self.ema.short).mean()
        data[EMA.MIDDLE] = data[CandleResponseDto.CLOSE].ewm(span=self.ema.middle).mean()
        data[EMA.LONG] = data[CandleResponseDto.CLOSE].ewm(span=self.ema.long).mean()

        data[MACD.UPPER] = data[EMA.SHORT] - data[EMA.MIDDLE]
        data[MACD.MIDDLE] = data[EMA.SHORT] - data[EMA.LONG]
        data[MACD.LOWER] = data[EMA.MIDDLE] - data[EMA.LONG]

        data[MACD.UP_INCREASE] = data[MACD.UPPER] > data[MACD.UPPER].shift(1)
        data[MACD.MID_INCREASE] = data[MACD.MIDDLE] > data[MACD.MIDDLE].shift(1)
        data[MACD.LOW_INCREASE] = data[MACD.LOWER] > data[MACD.LOWER].shift(1)

        return data

    def get_candle_data(self, candle_request_dto: CandleRequestDto):
        data = self.upbit_module.get_candles_data(candle_request_dto)
        data = self.create_sub_data(data=data)
        return data


    def save_data(self, candle_data: CandleData):
        self.candle_data_repository.save(candle_data)


