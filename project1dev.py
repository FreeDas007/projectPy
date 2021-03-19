import datetime as dt

date_format = '%d.%m.%Y'

class Record:
    def __init__(self, amount, comment, date=''):
        self.amount = amount
        self.comment = comment
        if date == '':
            self.date = dt.datetime.now().date()
        else:
            self.date = dt.datetime.strptime(date, date_format).date()
        self.list = [amount, comment, self.date]
        print('\tRecord', amount, comment, self.date, sep=':')
        
class Calculator:
    def __init__(self, limit):
        self.limit = limit
        self.records = []
        self.today = dt.datetime.now().date()
        _delta = dt.timedelta(days=7)
        self.beginweek = (dt.datetime.now() - _delta).date()
        print('init Calculator:', self.limit)
    def get_today_stats(self):
        # ск. денег/калорий потрачено сегодня
        _total=0
        for e in self.records:
            if e[2] == self.today:
                _total += e[0]
                print('\ttoday:', e[0], e[1], e[2])
        return _total
    def get_week_stats(self):
        # ск. денег/калорий потрачено за неделю
        _total=0
        for e in self.records:
            if e[2] >= self.beginweek and e[2] <= self.today:
                _total += e[0]
                print('\tweek:', e[0], e[1], e[2])
        return _total
    def add_record(self, rec):
        self.records.append(rec.list)
        if rec.list[2] == self.today:  # запись за сегодня - минусуем из limit
            self.limit = self.limit - int(rec.list[0])
        for e in self.records:  # отладочная печать
            print('\t', e)

class CashCalculator(Calculator):
    def __init__(self, limit):
        super().__init__(limit)
        self.currencies={'rub':' руб.', 'usd':' usd.', 'euro':' euro.'}
        self.currency_rate={'rub':1, 'usd':72, 'euro':88}
    def Ostatok(self, kolvo, currency):
        _ostatok=str(round(kolvo / self.currency_rate[currency],2))
        return _ostatok + self.currencies[currency]
    def get_today_cash_remained(self, currency):
        # на сегодня осталось в ...
        if self.limit < 0:
            valuta = self.currencies[currency]
            print("Денег нет, держись: твой долг -", self.limit, valuta)
        elif self.limit == 0:
            print('Денег нет, держись')
        else:
            return 'На сегодня осталось ' + self.Ostatok(self.limit, currency)
    def get_today_cash_stats(self, currency):
        # потрачено за сегодня
        print('Потрачено за сегодня ',
              self.Ostatok(self.get_today_stats(), currency))
    def get_week_cash_stats(self, currency):
        # потрачено за последние 7 дней
        _k = self.get_week_stats()
        _itogo=self.Ostatok(_k, currency)
        print('Потрачено за неделю ', _itogo)

class CaloriesCalculator(Calculator):
    # Калькулятор калорий
    def get_calories_remained(self):
        # на сегодня осталось в ...
        if self.limit <= 0:
            _k = -1 * self.limit
            print(f"Хватит есть! Ты перебрал ! {_k} Ккал!!!")
        else:
            print(f"Сегодня можно съесть что-нибудь ещё, но с общей калорийностью не более {self.limit} кКал")
    def get_today_calories_stats(self):
        # потрачено за сегодня
        _k = self.get_today_stats()
        print('Потрачено за сегодня ', _k, 'Ккал')
    def get_week_calories_stats(self):
        # потрачено за последние 7 дней
        _k = self.get_week_stats()
        print('За неделю сожгли', _k, 'Ккал')

# создадим калькулятор денег с дневным лимитом 1000
cash_calculator = CashCalculator(1000)
        
# дата в параметрах не указана, 
# так что по умолчанию к записи должна автоматически добавиться сегодняшняя дата
cash_calculator.add_record(Record(amount=145, comment="кофе")) 
# и к этой записи тоже дата должна добавиться автоматически
cash_calculator.add_record(Record(amount=300, comment="Серёге за обед"))
# а тут пользователь указал дату, сохраняем её
cash_calculator.add_record(Record(amount=3000, comment="бар в Танин др", date="08.11.2019"))
cash_calculator.add_record(Record(amount=400, comment="такси", date="11.03.2021"))
                
print(cash_calculator.get_today_cash_remained("rub"))
print(cash_calculator.get_today_cash_remained("usd"))
cash_calculator.get_today_cash_stats('rub')

cash_calculator.get_week_cash_stats('rub')
# должно напечататься # На сегодня осталось 555 руб

print('\nТестирование Калькулятора калорий\n')
# ----------------
# создадим калькулятор калорий дневным лимитом 2000
Calorie_calculator = CaloriesCalculator(2000)

Calorie_calculator.add_record(Record(amount=1186, comment="Кусок тортика. И ещё один.", date="24.02.2019")) 
Calorie_calculator.add_record(Record(amount=84, comment="Йогурт.", date="23.02.2019")) 
Calorie_calculator.add_record(Record(amount=1140, comment="Баночка чипсов.", date="24.02.2019")) 

Calorie_calculator.add_record(Record(amount=1186, comment="Кусок тортика. И ещё два.")) 
Calorie_calculator.add_record(Record(amount=84, comment="Йогурт жирный.")) 
Calorie_calculator.add_record(Record(amount=1140, comment="Чипсы ...")) 

Calorie_calculator.get_calories_remained()
Calorie_calculator.get_today_calories_stats()
Calorie_calculator.get_week_calories_stats()
