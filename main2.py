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
    
#Extract data from the html files 
data=[]
for root, dirs, files in os.walk(folder_path):
    for file in files:
        if file.endswith(".html"):
            file_path = os.path.join(root, file)
            with open(file_path, 'r', encoding='utf-8') as f:
                html = f.read()
                soup = BeautifulSoup(html, 'html.parser')
            
                #Extract the required information from the HTML using BeautifulSoup
                #Extract Date of Sale
                date_elem = soup.find('span', class_= 'hcl-label hcl-label--state hcl-label--sold-at')  
                date = date_elem.text.strip() if date_elem else ''
            
                #Extract the Address
                address_elem = soup.find('h2', class_='sold-property-listing__heading')  
                address = address_elem.text.strip() if address_elem else ''
                
                #Extract Location
                location_elem = soup.find('div', class_='sold-property-listing__location')  
                location = location_elem.text.strip() if location_elem else ''
                
                #Extract Boarea (Living Area)
                #boarea_elem = soup.find('div', class_='sold-property-listing__land-area')  
                #boarea = boarea_elem.text.strip() if boarea_elem else ''
                # Find the container with boarea, biarea, and rooms
                area_elem = soup.find('div', class_='sold-property-listing__subheading sold-property-listing__area')

                if area_elem:
                    # Extract and clean text
                    area_text = area_elem.text.strip()
                    
                    if area_text:
                        # Extract boarea (first number before '+')
                        try:
                            boarea = area_text.split()[0]
                        except IndexError:
                            boarea = None  # Handle case where boarea is not found

                        # Extract biarea (number after '+', if it exists)
                        biarea_elem = area_elem.find('span', class_='listing-card__attribute--normal-weight')
                        if biarea_elem and biarea_elem.text.strip():
                            biarea = biarea_elem.text.strip().replace('m²', '').replace('+', '').strip()
                        else:
                            biarea = None  #if no biarea found

                        # Extract rooms (number before 'rum')
                        try:
                            rooms = area_text.split()[-2]  #split text and take the second last part before 'rum'
                        except IndexError:
                            rooms = None  #handle case where rooms are not found
                    else:
                        boarea = biarea = rooms = None  #If area_text is empty
                else:
                    boarea = biarea = rooms = None  #If no element found
                                    
                #Calculate Total Area (Boarea + Biarea)
                totalarea = ''
                if boarea and biarea:
                    try:
                        boarea_val = int(boarea.replace('m²', '').strip())  # Remove "m²" and strip whitespace
                        biarea_val = int(biarea.replace('m²', '').strip())
                        totalarea = boarea_val + biarea_val
                    except ValueError:
                        totalarea = ''  #If the values can't be converted to integers, leave it blank
                
                #Extract the Number of Rooms
                #rooms_elem = soup.find('span', class_='number-of-rooms')  
                #rooms = rooms_elem.text.strip() if rooms_elem else ''
                
                #Extract the Closing Price
                price_elem = soup.find('span', class_='hcl-text hcl-text--medium')  
                price = price_elem.text.strip().replace('kr', '').replace(' ', '').replace('\u00a0', '') if price_elem else ''
                
                #Append the extracted data as a list to the 'data' list
                data.append([date, address, location, boarea, biarea, totalarea, rooms, price])

#Define the header for the CSV file
header = ['Date', 'Address', 'Location', 'Boarea', 'Biarea', 'Totalarea', 'Rooms', 'Price']

#Write the extracted data to a CSV file
csv_file = 'property_data.csv'
with open(csv_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(header)  #Write the header row
    writer.writerows(data)   #Write the data rows

print(f"Data written to {csv_file}.")