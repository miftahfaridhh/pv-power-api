from datetime import datetime
from datetime import date, timedelta

dateStart = '2022-01-01'

dsdt = datetime.strptime(dateStart, '%Y-%m-%d')

dsdt_1 = dsdt + timedelta(1)

print(dsdt, dsdt_1)