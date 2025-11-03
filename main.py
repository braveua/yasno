import requests
import json
import datetime
from datetime import timedelta

# URL = "https://app.yasno.ua/api/blackout-service/public/shutdowns/probable-outages?regionId=25&dsoId=902"
URL = "https://app.yasno.ua/api/blackout-service/public/shutdowns/regions/25/dsos/902/planned-outages"

def save_to_file(data, filename="blackout_data.json"):
    with open(filename, 'w') as json_file:
        json.dump(data, json_file, indent=4) # 'indent=4' for pretty-printing

def load_from_file(filename="blackout_data.json"):
    with open(filename, 'r') as json_file:
        return json.load(json_file)
    
def mm_to_hhmm(minutes: int) -> str:
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours:02}:{mins:02}"

def fetch_blackout_data(url):
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad responses
    json_data = response.json()
    save_to_file(json_data)
    return json_data


if __name__ == "__main__":
    # Fetch and save fresh data (can be commented out if using local file only)
    fetch_blackout_data(URL)
    data = load_from_file()
    today_slots = data.get("2.1").get("today").get("slots")
    tomorrow_slots = data.get("2.1").get("tomorrow").get("slots")
    date = data.get("2.1").get("today").get("date")
    date = datetime.datetime.fromisoformat(date)
    tomorrow_date = (date + timedelta(hours=24)).strftime("%d/%m/%Y")
    date = date.strftime("%d/%m/%Y")
    now = datetime.datetime.now().strftime("%d/%m/%Y")
    # print(f"{date=} {now=}")
    # print("Совпадает:", date == now)
    updatedOn = data.get("2.1").get("updatedOn")
    updatedOn = datetime.datetime.fromisoformat(updatedOn)
    updatedOn = updatedOn + timedelta(hours=3)
    updatedOn = updatedOn.strftime("%d/%m/%Y %H:%M")
    
    print("======================================")
    print("Дата планових отключений")

    print(f"Сегодня ({date}):")
    cnt = 0
    for slot in today_slots:
        if slot.get("type") == "NotPlanned":
            continue
        print(f" 🌑 Отключение: {mm_to_hhmm(slot.get('start'))} - {mm_to_hhmm(slot.get('end'))}")
        cnt += 1
    if cnt == 0:
        print(" 💡 Без отключений!")


    print(f"Завтра ({tomorrow_date}):")
    cnt = 0
    for slot in tomorrow_slots:
        if slot.get("type") == "NotPlanned":
            continue
        print(f" 🌑 Отключение: {mm_to_hhmm(slot.get('start'))} - {mm_to_hhmm(slot.get('end'))}")
        cnt += 1
    if cnt == 0:
        print(" 💡 Без отключений!")

    print(f"Обновлено в {updatedOn}")
    print("======================================")

    # print(mm_to_hhmm(870))   # Example usage
    # print(mm_to_hhmm(1140))  # Example usage
