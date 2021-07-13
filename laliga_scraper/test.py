from datetime import datetime
from pytz import timezone

def to_CET(value) -> str:
    dt = datetime.fromisoformat(value)
    cet = timezone('CET')
    dt = dt.astimezone(cet)
    return dt.strftime('%Y-%m-%d %H:%M:%S')



cet = to_CET('2021-03-17T18:00:00+00:00')
print(cet)