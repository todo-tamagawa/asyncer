import datetime
from decimal import Decimal
from pprint import pprint
from typing import ClassVar, List, Optional
from dataclasses import asdict, dataclass

from inflection import tableize

from masoniteorm.query import QueryBuilder
from masoniteorm.config import load_config
import pendulum
from pendulum.datetime import DateTime

from libs.api import ENDPOINT, call


@dataclass
class Resource:
    __table__: ClassVar[str] = ''
    __primary_key__: ClassVar[str] = "id"

    @classmethod
    def get_table_name(cls):
        return cls.__table__ or tableize(cls.__name__)

    @classmethod
    def get_primary_key(self):
        return self.__primary_key__

    def get_primary_key_value(self):
        return getattr(self, self.get_primary_key())

    def set_primary_key_value(self, value):
        return setattr(self, self.get_primary_key(), value)

    @classmethod
    def query(cls):
        return QueryBuilder(
            table=cls.get_table_name(),
            connection_details=cls.get_connection_details(),
        )

    @staticmethod
    def get_connection_details():
        return load_config().DB.get_connection_details()

    def save(self):
        if pkey := self.get_primary_key_value():
            pprint(pkey)
            print('FXIME')
            return self
        else:
            attributes = asdict(self)
            del attributes[self.get_primary_key()]
            query_result = self.query().create(attributes, id_key=self.get_primary_key())
            self.set_primary_key_value(query_result[self.get_primary_key()])
            return self

    @classmethod
    def bulk_save(cls, rows: List['Resource']):
        def attr(row: 'Resource'):
            attributes = asdict(row)
            del attributes[row.get_primary_key()]
            return attributes
        creates = [attr(row) for row in rows]
        cls.query().bulk_create(creates)

    @classmethod
    def truncate(cls):
        cls.query().truncate()

    @classmethod
    def find(cls, record_id: int):
        data = cls.query().where(cls.get_primary_key(), record_id).first()
        return cls(**data)

    @classmethod
    def last(cls):
        data = cls.query().last('id')
        return cls(**data)

    @classmethod
    def to_pendulum(cls, value):
        if not value:
            return None
        elif isinstance(value, DateTime):
            return value
        elif isinstance(value, datetime.datetime):
            return pendulum.instance(value, tz='UTC')
        elif isinstance(value, str):
            return pendulum.parse(value, tz='UTC')
        return None


@dataclass
class Ticker(Resource):
    id: int = 0
    best_ask: float = 0
    best_ask_size: float = 0
    best_bid: float = 0
    best_bid_size: float = 0
    ltp: float = 0
    market_ask_size: float = 0
    market_bid_size: float = 0
    product_code: str = ''
    state: str = ''
    tick_id: int = 0
    timestamp: str = ''
    total_ask_depth: float = 0
    total_bid_depth: float = 0
    volume: float = 0
    volume_by_product: float = 0

    @classmethod
    async def load(cls):
        data = await call(ENDPOINT.Ticker)
        return Ticker(**data)


@dataclass
class Transaction(Resource):
    id: int = 0
    exchange: str = ''
    side: str = ''
    channel: str = ''
    price: float = 0
    volume: float = 0
    timestamp: Optional[DateTime] = None

    def __post_init__(self):
        self.timestamp = self.to_pendulum(self.timestamp)

    @classmethod
    def fetchAtRange(cls, min_time: str, max_time: str, exchange: str, channel: str):
        datas = cls.query()\
            .where('exchange', exchange)\
            .where('channel', channel)\
            .where('timestamp', '>=', min_time)\
            .where('timestamp', '<', max_time)\
            .get()
        return [Transaction(**data) for data in datas]


@dataclass
class Stack(Resource):
    id: int = 0
    exchange: str = ''
    channel: str = ''
    price: int = 0
    volume: Decimal = Decimal(0)
    timestamp: DateTime = pendulum.now()

    def __post_init__(self):
        self.volume = Decimal(self.volume)
        self.timestamp = self.to_pendulum(self.timestamp)

    @classmethod
    def fetchAtRange(cls, min_time: str, max_time: str, exchange: str, channel: str):
        datas = cls.query()\
            .where('exchange', exchange)\
            .where('channel', channel)\
            .where('timestamp', '>=', min_time)\
            .where('timestamp', '<', max_time)\
            .get()
        return [Stack(**data) for data in datas]

    @classmethod
    def getPriceRangeAtTimestamp(cls, timestamp: str, exchange: str, channel: str):
        query = cls.query()\
            .where('exchange', exchange)\
            .where('channel', channel)\
            .where('timestamp', timestamp)
        query.aggregate("MIN", "{column}".format(column='price'), 'min')
        query.aggregate("MAX", "{column}".format(column='price'), 'max')
        data = query.first()
        return (data.get('min'), data.get('max'))
