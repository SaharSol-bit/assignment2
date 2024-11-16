import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import seaborn as sns
import pandas as pd
import numpy as np
#import tarfile
import csv
import os

folder_path = r"C:\Users\sahar\OneDrive\Documents\GitHub\assignment2\kungalv_slutpriser"


#Check if the folder exists
if os.path.isdir(folder_path):
    print("Processing HTML files in the folder...")
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".html"):
                file_path = os.path.join(root, file)
                print(f"Found HTML file: {file_path}")
                #Perform some operation on each HTML file
                with open(file_path, 'r', encoding='utf-8') as f:
                    html = f.read()
                    print(f"Read {len(html)} characters from {file}.")
else:
    print(f"{folder_path} is not a valid folder.")
    
#extract data from the HTML files
data = []
for root, dirs, files in os.walk(folder_path):
    for file in files:
        if file.endswith(".html"):
            file_path = os.path.join(root, file)
            with open(file_path, 'r', encoding='utf-8') as f:
                html = f.read()
                soup = BeautifulSoup(html, 'html.parser')
                
                #find all house sale entries
                house_entries = soup.find_all('li', class_='sold-results__normal-hit')
                
                #process each house entry
                for entry in house_entries:
                    #extract Date of Sale
                    date_elem = entry.find('span', class_='hcl-label hcl-label--state hcl-label--sold-at')
                    date = date_elem.text.strip() if date_elem else ''
                    
                    #extract Address
                    address_elem = entry.find('h2', class_='sold-property-listing__heading')
                    address = address_elem.text.strip() if address_elem else ''
                    
                    #extract Location
                    location_elem = entry.find('div', class_='sold-property-listing__location')
                    if location_elem:
                        location_parts = location_elem.text.strip().split('\n')
                        location = location_parts[-1].strip()  #get the last line containing the location
                    else:
                        location = ''
                    
                    #extract Boarea, Biarea, and Rooms
                    area_elem = entry.find('div', class_='sold-property-listing__subheading sold-property-listing__area')
                    if area_elem:
                        area_text = area_elem.text.strip()
                        if area_text:
                            boarea = area_text.split()[0]
                            biarea_elem = area_elem.find('span', class_='listing-card__attribute--normal-weight')
                            biarea = biarea_elem.text.strip().replace('m²', '').replace('+', '').strip() if biarea_elem else ''
                            rooms = area_text.split()[-2] if 'rum' in area_text else ''
                        else:
                            boarea = biarea = rooms = ''
                    else:
                        boarea = biarea = rooms = ''
                    
                    #calculate Total Area
                    try:
                        boarea_val = int(boarea) if boarea else 0
                        biarea_val = int(biarea) if biarea else 0
                        totalarea = boarea_val + biarea_val
                    except ValueError:
                        totalarea = ''
                    
                    #extract the Closing Price
                    price_elem = entry.find('span', class_='hcl-text hcl-text--medium')
                    if price_elem:
                        price_text = price_elem.text.strip()
                        price = price_text.replace('Slutpris', '').replace('kr', '').replace(' ', '').replace('\u00a0', '')
                    else:
                        price = ''
                    
                    #append extracted data to the list
                    data.append([date, address, location, boarea, biarea, totalarea, rooms, price])

#define the header for the CSV file
header = ['Date', 'Address', 'Location', 'Boarea', 'Biarea', 'Totalarea', 'Rooms', 'Price']

#write the extracted data to a CSV file
csv_file = 'property_data.csv'
with open(csv_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(header)  #write the header row
    writer.writerows(data)   #write the data rows

print(f"Data written to {csv_file}.")
