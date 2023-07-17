from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd
from time import sleep
from tqdm import tqdm
import numpy as np

url = "https://torob.com/browse/99/%D9%84%D9%BE-%D8%AA%D8%A7%D9%BE-%D9%88-%D9%86%D9%88%D8%AA-%D8%A8%D9%88%DA%A9-laptop/"

driver = webdriver.Chrome()
driver.maximize_window()
driver.get(url)
sleep(60)

descriptions = []
stock_status = []
links = []
prices = []
name = []

content = driver.page_source
bs = BeautifulSoup(content, 'html.parser')
for a in bs.findAll('a', href=True):
    if a.find('div', attrs={'class':'filter-brand-item'}) is not None:
        brand = a.find_all('div', attrs={'class':'filter-brand-item'})
        name.append(brand[0].text.lower())
        name.append(brand[1].text.lower())

    if a.find('h2', attrs={'class':'product-name'}) is not None:
        title = a.find('h2', attrs={'class':'product-name'})
        status = a.find('div', attrs={'class':'badge'})
        price = a.find('div', attrs={'class':'product-price-text'})
        link = 'https://torob.com'+a['href']
        descriptions.append(title.text.lower())
        if status is not None:
            stock_status.append('stock')
        else:
            stock_status.append('new')
        links.append(link)
        prices.append(price.text)
name.extend(['مک بوک ایر',
         'macbook air',
         'مک بوک پرو',
         'macbook pro'])
brand = []
weight = []
cpu_series = []
cpu_model = []
cache = []
ram = []
memory = []
memory_type = []
size = []
ram_title = ['حافظه رم (Ram)',
             'حافظه رم',
             'ظرفیت حافظه RAM',
             'مقدار حافظه رم',
             'ظرفیت حافظه RAM',
             'مقدار حافظه رم',
             'ظرفیت حافظه ی رم',
             'میزان حافظه رم'
             ]
memory_title = ['ظرفیت حافظه داخلی',
                'ظرفیت SSD',
                'ظرفیت حافظه HDD',
                'ظرفیت حافظه SSD',
                'حافظه خشک(SSD)',
                'حافظه مکانیکی(HDD)',
                'ظرفیت HDD',
                'هارد دیسک'
                ]

for d in descriptions:
    b = False
    for n in name:
        if n in d and not b:
            b = True
            brand.append(n)
            break
    if not b:
        brand.append('unknown')
        
print('brand:', len(brand))
print('first 10 brand: ', brand[:10])

option = webdriver.ChromeOptions()
option.add_argument('--headless')
for link in tqdm(links):
    driver = webdriver.Chrome(options=option)
    driver.get(link)
    content = driver.page_source
    bs = BeautifulSoup(content, 'html.parser')
    specification = bs.find('div', attrs={'class':'specs-content'})
    if specification.find('div', attrs={'class':'no-specs'}) is None:
        titles = specification.find_all('div', attrs={'class':'detail-title'})
        values = specification.find_all('div', attrs={'class':'detail-value'})
        w = False
        cps = False
        cpm = False
        ca = False
        s = False
        r = False
        m = False
        mt = False
        for title, value in zip(titles, values):
            if title.text.find('وزن') != -1 and not w:
                w = True
                weight.append(value.text)
            elif title.text == 'سری پردازنده' and not cps:
                cps = True
                cpu_series.append(value.text)
            elif (title.text == 'مدل پردازنده' or title.text == 'مدل پردازنده مرکزی') and not cpm:
                cpm = True
                cpu_model.append(value.text)
            elif (title.text.find('حافظه کش') != -1 or title.text.find('Cache') != -1) and not ca:
                ca = True
                cache.append(value.text)
            elif (title.text.find('اینچ') != -1 or value.text.find('اینچ') != -1) and not s:
                s = True
                size.append(value.text)
            elif title.text in ram_title and not r:
                r = True
                ram.append(value.text)
            elif title.text in memory_title and not m:
                if value.text != 'ندارد':
                    m = True
                    memory.append(value.text)
            elif (title.text.find('SSD') != -1 or value.text.find('SSD') !=-1) and not mt:
                if value.text != 'ندارد':
                    mt = True
                    memory_type.append('SSD')
        if not w:
            weight.append(np.nan)
        if not cps:
            cpu_series.append(np.nan)
        if not cpm:
            cpu_model.append(np.nan)
        if not ca:
            cache.append(np.nan)
        if not s:
            size.append(np.nan)
        if not r:
            ram.append(np.nan)
        if not m:
            memory.append(np.nan)  
        if not mt:
            memory_type.append('HDD')  
    else:
        weight.append(np.nan)
        cpu_series.append(np.nan)
        cpu_model.append(np.nan)
        cache.append(np.nan)
        size.append(np.nan)
        ram.append(np.nan)
        memory.append(np.nan)
        memory_type.append('HDD')

print('weight:', len(weight))
print('cpu series:', len(cpu_series))
print('cpu model:', len(cpu_model))
print('cache:', len(cache))
print('size:', len(size))
print('ram:', len(ram))
print('memory:', len(memory))
print('memory type:', len(memory_type))

df1 = pd.DataFrame({'Title':descriptions, 'stock_status':stock_status, 'prices':prices})
df1.to_csv('data.csv', index=False, encoding='utf-8')

df2 = pd.DataFrame({'Title':descriptions, 'Link': links})
df2.to_csv('links.csv', index=False, encoding='utf-8')

df3 = pd.DataFrame({'Title':descriptions, 'Brand':brand, 'Weight':weight, 'CPUSeries':cpu_series, 'CPUModel':cpu_model, 'Cache':cache, 'RAM':ram, 'Memory':memory, 'MemoryType':memory_type, 'Size':size, 'StockStatus':stock_status, 'Price':prices})
df3.to_csv('laptop.csv', index=False, encoding='utf-8')