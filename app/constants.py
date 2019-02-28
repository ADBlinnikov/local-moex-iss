MARKETS = {
    "stock": [
        "index",  # Индексы фондового рынка
        "shares",  # Рынок акций
        "bonds",  # Рынок облигаций
        "ndm",  # Режим переговорных торгов
        "otc",  # ОТС
        "ccp",  # Репо с цк
        "deposit",  # Депозиты с ЦК
        "repo",  # Рынок сделок РЕПО
        "qnv",  # Квал.инвесторы
        "moexboard",
        "classica",
        "standard",
    ],
    "state": [
        "index",  # Индексы ГКО и ОФЗ
        "bonds",  # Облигации ГЦБ
        "repo",  # Междилерское РЕПО
        "ndm",  # Внесистемные сделки
    ],
    "currency": [
        "basket",  # Бивалютная корзина
        "selt",  # Биржевые сделки с ЦК
        "futures",  # Поставочные фьючерсы
    ],
    "futures": [
        "main",  # Срочные инструменты
        "forts",  # ФОРТС
        "options",  # Опционы ФОРТС
    ],
    "commodity": ["futures"],  # Секция стандартных контрактов НТБ
    "interventions": ["grain"],  # Закупочные интервенкии по зерну
}

HISTORY_COLUMNS: dict = {
    "secid": "str",
    "open": "float",
    "high": "float",
    "low": "float",
    "close": "float",
    "volume": "int",
    "value": "float",
    "openposition": "int",
    "openpositionvalue": "float",
}

OPTION_CODE = r"""
    (?P<underlying_code>\w{2})
    (?P<strike>\d*\.?\d*)
    (?P<settlement_type>[AB])
    (?P<settlement_month>\w)
    (?P<settlement_year>\d)
    (?P<weekly>[ABDE]?)
    """


CALL_MONTH = "ABCDEFGHIJKL"
PUT_MONTH = "MNOPQRSTUVWX"


ESTIMATORS = [
    "CloseToClose",
    "Parkinson",
    "GarmanKlass",
    "RogersSatchell",
    "HodgesTompkins",
    "YangZhang",
]
