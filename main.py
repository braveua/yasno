import requests
import json
import redis
from datetime import datetime
from typing import Any
# import pytz

URL = "https://app.yasno.ua/api/blackout-service/public/shutdowns/regions/25/dsos/902/planned-outages"
master_service_name = 'myredis'
sentinels = [
    ('192.168.0.5',  26379),
    ('192.168.0.41', 26379),
]
data = None
ex = 1200
# master_address = client.discover_master(master_service_name) # возвращает(ip, port) клиента redis

def read_url():
    # print("loading URL")
    data = json.loads(requests.get(URL).text)
    write_redis(data)
    return data

def write_redis(data):
    client = redis.Sentinel(sentinels, socket_timeout=0.1, )
    master = client.master_for('myredis', redis_class=redis.Redis)
    master.set("yasno_data", json.dumps(data,), ex=ex)

def read_redis()->dict[str, Any]|None:
    # print("loading Redis")
    client = redis.Sentinel(sentinels, socket_timeout=0.1, )
    master = client.master_for('myredis', redis_class=redis.Redis)
    data = master.get("yasno_data")
    return json.loads(data) if data else None # type: ignore

def get_data()->dict[str, Any]|None:
    data = read_redis()
    if not data:
        data = read_url()
    return data # type: ignore

def get_date(date) -> str:
    date = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S%z")
    date = datetime.strftime(date,"%d.%m.%Y")
    return date

def get_datetime(date) -> str:
    dt_local = datetime.fromisoformat(date).astimezone()
    dt_local = datetime.strftime(dt_local, "%d.%m.%Y %H:%M")    
    return dt_local

def mm_to_hhmm(minutes: int) -> str:
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours:02}:{mins:02}"

def get_slot_data(slots, status):
    # print(status)
    if status == "ScheduleApplies":
        cnt = 0
        for slot in slots:
            if slot.get("type") == "NotPlanned":
                continue
            print(f" 🌑 Отключение: {mm_to_hhmm(slot.get('start'))} - {mm_to_hhmm(slot.get('end'))}")
            cnt += 1
        if cnt == 0:
            print(" 💡 Без отключений!")
    if status == "WaitingForSchedule":
        print(" ⏳ График ожидается...")

def main():
    data = get_data() 
    # updateOn = data.get("2.1").get("updatedOn")
    group = data.get("2.1") # type: ignore

    today_shedule = group.get("today")           # type: ignore
    tomorrow_shedule = group.get("tomorrow")           # type: ignore
    
    today = today_shedule.get("date")       # type: ignore
    tomorrow = tomorrow_shedule.get("date")       # type: ignore
    
    today = get_date(today)
    tomorrow = get_date(tomorrow)
    
    today_status = today_shedule.get("status")
    tomorrow_status = tomorrow_shedule.get("status")


    today_slots = group.get("today").get("slots")       # type: ignore
    tomorrow_slots = group.get("tomorrow").get("slots") # type: ignore
    
    # tomorrow = group.get("tomorrow").get("date")        # type: ignore
    
    
    updated = group.get("updatedOn")                    # type: ignore
    updated = get_datetime(updated)

    print("==================================")
    print("   График планових отключений")
    print("----------------------------------")
    print(f"   Сегодня ({today}):")
    get_slot_data(today_slots, today_status)
    print(f"   Завтра  ({tomorrow}):")
    get_slot_data(tomorrow_slots, tomorrow_status)
    print(f"   Обновлено в {updated}")
    print("==================================")


    # print(group)
    # print(today)
    # print(tomorrow)
    # print(updated)
    # print(today_status)
    # print(tomorrow_status)
    # print(group.get("tomorrow"))

if __name__ == "__main__":
    main()

