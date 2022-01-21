import csv
import time
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options

#%% Read existing data of available urls

filename = "href_allaround_final.csv" # consider changing into 'href_greece'

df_href = pd.read_csv(filename)

# Use slicing in case of errors while parsing
# df_href = df_href[:10]
# df_href = df_href[142:]

#%% Function that reads dictionary, key and returns the value or "NaN"
def exist(dictionary, key_v):
    try:
        temporary_value = dictionary[key_v]
    except KeyError:
        temporary_value = "NaN"
    return temporary_value

def emptydata():
    data = [('Παροχές ξενοδοχείου', 'NaN'), ('Χαρακτηριστικά δωματίου', 'NaN'), ('Τύποι δωματίων', 'NaN'),
                ('Τοποθεσία', 'NaN'), ('Καθαριότητα', 'NaN'), ('Εξυπηρέτηση', 'NaN'), ('Αξία', 'NaN'),
                ('Αριθμός κριτικών', 'NaN'), ('Διεύθυνση', 'NaN'), ('Περιγραφή', 'NaN')]
    return data

def restart_driver(driver, options):
    driver.close()
    driver = webdriver.Firefox(options=options)
    return driver

#%% Main loop after initializing the webdriver

options = Options()
options.page_load_strategy = 'eager'

driver = webdriver.Firefox(options=options)

# Open a file to save after each iteration the scraped data
csvFile = open('tripadvisor_allaround_final.csv', "a", encoding="utf-8", newline='')
csvWriter = csv.writer(csvFile, delimiter=',')

# Define the main domain url. This url is expanded with the urls read above
base_url = 'https://www.tripadvisor.com.gr'

# Total amenities list is the major list that will contain the outcomes of each iteration. It should contain the same number of elements as the dataframe (df_href)
total_amenities = []
counter = 0

# Main loop
for ele in df_href['url']:
    final_url = base_url + ele
    driver.get(final_url)
    time.sleep(1)
    
    data = []
    
    try:
        driver.find_element(By.XPATH, "//button[contains(text(),'Εντάξει')]").click()
    except:
        pass
    
    try:
        html_source = driver.page_source
        soup = BeautifulSoup(html_source)
    except:
        data = emptydata()
        total_amenities.append(data)
        print('url {} was not reached'.format(final_url))
        print('driver restarts')
        driver = restart_driver(driver, options)
        continue

    time.sleep(1)
    
    if not soup:
        data = emptydata()
        total_amenities.append(data)
        print('url {} was skipped'.format(final_url))
        counter+=1
        continue


    # Scrape Description (if available)
    description1 = soup.find("div", class_="duhwe _T bOlcm bWqJN Ci")
    description2 = soup.find("div", class_="duhwe _T bOlcm bWqJN Ci dMbup")

    if description1 and description2:
        print('Alert')
        print('url {} has both descriptions, consider reformatting'.format(final_url))

    if description1:
        description = description1.get_text()
    elif description2:
        description = description2.get_text()
    else:
        description = "NaN"


    # Scrape Amenities and try to match them witch categories
    amenities_data = soup.find_all("div", class_="exmBD K")
    ams = []
    for el in amenities_data:
        ams.append(el.get_text("|", strip=True))

    categories = soup.find_all("div", class_="ccdzg S5 b Pf ME")
    ams_categories = []
    for el in categories:
        ams_categories.append(el.get_text())
    
    # We do not need the part "Χρήσιμες πληροφορίες" that is collected through class="ccdzg S5 b Pf ME" and thus we remove it
    to_remove = "Χρήσιμες πληροφορίες"
    if to_remove in ams_categories: ams_categories.remove(to_remove)
    
    
    # ZIP Amenities with Categories of Amenities if their length is equal.
    if len(ams_categories) != len(ams):
        # amenities = []                                                                                      # consider removing
        data.append(('Παροχές ξενοδοχείου', 'NaN'))
        data.append(('Χαρακτηριστικά δωματίου', 'NaN'))
        data.append(('Τύποι δωματίων', 'NaN'))
    else:
        amenities = dict(list(zip(ams_categories, ams)))
        # 1
        tempvalue = exist(amenities, "Παροχές ξενοδοχείου")
        data.append(('Παροχές ξενοδοχείου', tempvalue))
        # 2
        tempvalue = exist(amenities, "Χαρακτηριστικά δωματίου")
        data.append(("Χαρακτηριστικά δωματίου", tempvalue))
        # 3
        tempvalue = exist(amenities, "Τύποι δωματίων")
        data.append(("Τύποι δωματίων", tempvalue))


    # Scrape Location and Number of Reviews
    try:
        location = soup.find("span", class_="ceIOZ yYjkv").get_text()
    except AttributeError:
        location = 'NaN'
    try:
        number_of_reviews = soup.find("span", class_="HFUqL").get_text()
    except AttributeError:
        number_of_reviews = 'NaN'
        

    # Scrap Ratings (ratings were found in two different classes -  afterall they are combined)
    rating123 = soup.find_all("div", class_="cmZRz f")
    rating4 = soup.find_all("div", class_="cmZRz f dfnfs")
    rating = rating123 + rating4
    ratings = []
    if rating:
        for ele in rating:
            desc = ele.find("div", class_="bjRcr").get_text()
            rate = ele.find("span").get("class")[1][-2:]
            ratings.append((desc, rate))
        d_ratings = dict(ratings)
        #1
        tempvalue = exist(d_ratings, "Τοποθεσία")
        data.append(("Τοποθεσία", tempvalue))
        #2
        tempvalue = exist(d_ratings, "Καθαριότητα")
        data.append(("Καθαριότητα", tempvalue))
        #3
        tempvalue = exist(d_ratings, "Εξυπηρέτηση")
        data.append(("Εξυπηρέτηση", tempvalue))
        #4
        tempvalue = exist(d_ratings, "Αξία")
        data.append(("Αξία", tempvalue))
    else:
        print('no ratings')
        data.append(('Τοποθεσία', 'NaN'))
        data.append(('Καθαριότητα', 'NaN'))
        data.append(('Εξυπηρέτηση', 'NaN'))
        data.append(('Αξία', 'NaN'))
    
    try:
        #location_name = soup.find("div", class_="KeVaw").get_text().split()[-1]
        location_name = soup.find("div", class_="KeVaw").get_text()
    except:
        location_name = "NaN"
        
    # Now append all the rest info that have been scraped above
    data.append(("Αριθμός κριτικών", number_of_reviews))
    data.append(("Διεύθυνση", location))
    data.append(("Προορισμός", location_name))
    data.append(("Περιγραφή", description))
    
    total_amenities.append(data)
    csvWriter.writerow(data)
    counter+=1
    print("So far {} urls have been processed".format(counter))
    time.sleep(1)

driver.close()
csvFile.close()




