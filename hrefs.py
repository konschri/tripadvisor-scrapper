import csv
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
import pandas as pd
import re


START = time.time()

filename = 'href_allaround.csv'
csvFile = open(filename, "a", encoding="utf-8", newline='')
csvWriter = csv.writer(csvFile, delimiter=',')


urls_dict = {"Αθήνα": 'https://www.tripadvisor.com.gr/Hotels-g189400-Athens_Attica-Hotels.html', #906 results
             "Θεσσαλονίκη": 'https://www.tripadvisor.com.gr/Hotels-g189473-Thessaloniki_Thessaloniki_Region_Central_Macedonia-Hotels.html', #205 results
             "Κρήτη": 'https://www.tripadvisor.com.gr/Hotels-g189413-Crete-Hotels.html', #5202 results
             "Κυκλάδες": 'https://www.tripadvisor.com.gr/Hotels-g189422-Cyclades_South_Aegean-Hotels.html', #5747 results
             "Ιόνια Νησιά": 'https://www.tripadvisor.com.gr/Hotels-g189456-Ionian_Islands-Hotels.html', #5051 results
             "Πελοπόννησος": 'https://www.tripadvisor.com.gr/Hotels-g189483-Peloponnese-Hotels.html', #2041 results
             "Σποράδες": 'https://www.tripadvisor.com.gr/Hotels-g189497-Sporades-Hotels.html', #938 results      
             }


options = Options()
options.page_load_strategy = 'eager'
driver = webdriver.Firefox(options=options)

for key in urls_dict:
    url = urls_dict[key]


    driver.get(url)
    try:
        driver.find_element(By.XPATH, "//button[contains(text(),'Εντάξει')]").click()
    except:
        pass
    
    html_source = driver.page_source
    soup = BeautifulSoup(html_source, features="lxml")
    
    # find num pages
    try:
        total_results = soup.find("span", class_="eMoHQ").text
        total_results = int(re.sub("[^0-9]", "", total_results))
        print('1')
    except AttributeError:
        try:
            total_results = soup.find("div", class_="cIUfa Ci").text
            total_results = total_results[:-4].strip()
            total_results = int(re.sub("[^0-9]", "", total_results))
            print('2')
            print(total_results)
        except:
            total_results = 100
                    
    
    # we divide the total results for each city based on the default value of 30 items per page
    num_pages = 1 + (total_results // 30)
    #total_results = find_element_by_xpath(".//span[@class='eMoHQ']").text
    print(total_results)
    
    for i in range(num_pages):
        data = soup.find_all("div", class_="listing_title")
        price_data = soup.find_all("div", {"data-clickpart":"chevron_price"})
        
        print('page number: ', i+1)
        print("We got {} values for titles and {} for prices".format(len(data), len(price_data)))
        
        for i in range(len(data)):
            time.sleep(1)
            
            a_data = data[i].find("a")
            Link = a_data.get('href')
            Id = a_data.get('id')
            try:
                price = price_data[i].get_text()
            except IndexError:
                price = "0"
            name = a_data.get_text().strip()
            csvWriter.writerow([Id, Link, name, price])
            print(Id, Link, name, price)
        
        attempts = 0
        while attempts < 3:
            try:
                #driver.find_element_by_xpath('.//span[@class="nav next ui_button primary"]').click()
                driver.find_element_by_xpath('.//a[@class="nav next ui_button primary"]').click()  # Remember to change a/span according to needs
                time.sleep(3)
                break
            except:
                driver.refresh()
                attempts +=1
        
        if attempts == 3:
            print("Did not manage to move into next num page. Quitting...")
            quit()
        
        html_source = driver.page_source
        soup = BeautifulSoup(html_source)
        if not soup:
            print('we skipped num page {}'.format(i))
            continue
        
        tempEND = time.time()
        print('Num page {} finished in {}'.format(i, tempEND-START))
        
csvFile.close()
driver.close()

END = time.time()
print("Total execution time {}".format(END-START))


#%% Block 2 - Basic preprocess on file created at Block 1

colnames = ["property_id", "url", "name", "price"]
df_href = pd.read_csv(filename, names=colnames, header=None)

# Check for duplicates and drop
print("Initially we have {} instances. There are {} duplicates which are removed.".format(len(df_href), df_href.duplicated().sum()))
df_href.drop_duplicates(inplace=True)
print("The final length of dataframe to be considered is {}.".format(len(df_href)))

df_href['property_id'] = [int(x.split('_')[1]) for x in df_href['property_id']] # consider removing int() if want to keep id as string

df_href['urlinfo'] = [x.split('-') for x in df_href['url']]
df_href['gcode'] = [x[1] for x in df_href['urlinfo']]
df_href['dcode'] = [x[2] for x in df_href['urlinfo']]
df_href = df_href.drop(['urlinfo'], axis=1)

df_href.to_csv("href_allaround_final.csv", header=True, index=False) # HERE REPLACE WITH VAR FILENAME - for experimenting reasons keep a different file name






