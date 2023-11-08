# load URL and parse it
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import re
import time
import random

'''
TODO: 
1. Обработать случай, когда расписание не загрузилось (сервер ТПУ упал)
2. Сохранение расписания в файл и его загрузка при запуске программы
3. Убедиться, что изменение расписания отрабатывается корректно
4.
'''

# load URL and parse it
def rasp_parse(url):
    try:
        r = requests.get(url)
    except requests.exceptions.ConnectionError:
        return None
    
    # parse HTML
    soup = BeautifulSoup(r.text, 'html.parser')

    rasp_table = soup.find('div', {'id': 'raspisanie-table'})
    rasp_table = rasp_table.find('tbody')
    tr_list = rasp_table.find_all('tr')

    monday, tuesday, wednesday, thursday, friday, saturday = [], [], [], [], [], []
    for tr_day in tr_list:
        monday.append(tr_day.find_all('td')[1])
        tuesday.append(tr_day.find_all('td')[2])
        wednesday.append(tr_day.find_all('td')[3])
        thursday.append(tr_day.find_all('td')[4])
        friday.append(tr_day.find_all('td')[5])
        saturday.append(tr_day.find_all('td')[6])

    df = pd.DataFrame(columns=['time', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'])
    df['time'] = ['8:30-10:05', 
                  '10:25-12:00', 
                  '12:40-14:15', 
                  '14:35-16:10', 
                  '16:30-18:05', 
                  '18:25-20:00', 
                  '20:20-21:55']
    
    for i in range(len(monday)):
        df['monday'][i] = monday[i].text
        df['tuesday'][i] = tuesday[i].text
        df['wednesday'][i] = wednesday[i].text
        df['thursday'][i] = thursday[i].text
        df['friday'][i] = friday[i].text
        df['saturday'][i] = saturday[i].text

    df = df.replace(r'\n', ' ', regex=True)
    df.index = np.arange(1, len(df) + 1)
    return df
    
def check_dataframes(df_stable, df_new, week):
    if df_stable.equals(df_new):
        print(time.strftime("%H:%M:%S", time.localtime()), f'No changes for week {week}')
        return False # no changes
    else:
        print(time.strftime("%H:%M:%S", time.localtime()), f'Changes detected for week {week}')
        print('MISMATCHED VALUES:')
        for i in range(len(df_stable)):
            for j in range(len(df_stable.columns)):
                if df_stable.iloc[i, j] != df_new.iloc[i, j]:
                    print('row =', i+1, 'column =', j+1, 'value =', df_stable.iloc[i, j])
        return True # changes detected

def main(week, weeks_ahead, user = 506784):
    #url = 'https://rasp.tpu.ru/user_'+ str(user) + '/2023/' + str(week) + '/view.html?is_archive=0'
    df_stable = [] # 0 - current week, 1 - next week, 2 - next next week, 3 - next next next week
    for i in range (weeks_ahead):
        url = 'https://rasp.tpu.ru/user_'+ str(user) + '/2023/' + str(week + i) + '/view.html?is_archive=0'
        df_stable.append(rasp_parse(url))
        time.sleep(random.randint(5, 10)) # to avoid dead TPU server
    print('Stable schedule loaded')

    changed_schedule = False
    while True:
        time.sleep(random.randint(60, 120)) # 1-2 min sleep - wait for new schedule
        df_new = []
        for i in range (weeks_ahead):
            url = 'https://rasp.tpu.ru/user_'+ str(user) + '/2023/' + str(week + i) + '/view.html?is_archive=0'
            df_stable.append(rasp_parse(url))
            time.sleep(random.randint(5, 10)) # to avoid dead TPU server
        for i in range(4):
            changed_schedule = check_dataframes(df_stable[i], df_new[i], week + i)
            if changed_schedule:
                df_stable[i] = df_new[i]
                changed_schedule = False
                break

if __name__ == '__main__':
    week = 12
    user = 506784
    weeks_ahead = 4
    main(week, weeks_ahead, user)
