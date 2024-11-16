import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import seaborn as sns
import pandas as pd
import numpy as np
import tarfile
import csv
import os
import urllib.request
import requests


# Parse the html content
#soup= BeautifulSoup(html_content, 'html.parser')
folder_path = r'C:\Users\sahar\OneDrive\Documents\GitHub\assignment2\kungalv_slutpriser'

# Loop through all files in the folder
def process_folder(folder_path):
    extract_data = []
    for filename in os.listdir(folder_path):
        # Check if the file has an .html extension
        if filename.endswith('.html'):
            # Construct the full file path
            file_path = os.path.join(folder_path, filename)
            
            # Open and read the file
            with open(file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
                
            data= extract_data(html_content)
            extract_data.append(data)
    return html_content


# Extract data from the html content
def extract_data(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    data = {}

    # Extract date of sale
    date_elem = soup.find('div', class_='sold-property__land-date')
    data['date'] = date_elem.text.strip().split(' ', 1)[1] if date_elem else ''
        
    # Extract address
    address_elem = soup.find('h1', class_='sold-property__heading')
    data['address'] = address_elem.text.strip() if address_elem else ''

    # Extract location
    location_elem = soup.find('div', class_='sold-property__listing-location')
    if location_elem:
        data['location'] = location_elem.text.strip()

    # Extract area information
    area_elem = soup.find('div', class_='sold-property-listing__land-area')
    if area_elem:
        area_text = area_elem.text.strip()
        boarea = biarea = 0
        if '+' in area_text:
            boarea, biarea = map(int, area_text.split('+'))
        else:
            boarea = int(area_text.split()[0])
        data['boarea'] = boarea
        data['biarea'] = biarea
        data['total_area'] = boarea + biarea if biarea else ''

    # Extract number of rooms
    rooms_elem = soup.find('div', class_='sold-property__land-rooms')
    data['rooms'] = rooms_elem.text.strip().split()[0] if rooms_elem else ''


    # Extract plot area
    plot_elem = soup.find('div', class_='sold-property__metadata-item--land-area')
    data['plot_area'] = plot_elem.text.strip().split()[0] if plot_elem else ''

    # Extract closing price
    price_elem = soup.find('div', class_='sold-property__price')
    if price_elem:
        data['closing_price'] = price_elem.text.strip().split()[0].replace(' ', '')

    return data

# Process the tar file to extract data
def process_tar_file(tar_filename): 
    data=[]
    with tarfile.open(tar_filename, mode='r:gz') as tar:
        for member in tar.getmembers():
            if member.isfile() and member.name.endswith('.html'):
                f = tar.extractfile(member)
                html_content = f.read()
                extracted_data = extract_data(html_content)
                data.append(extracted_data)
    return data

tar_filename = 'kungalv_slutpriser.tar.gz'
output_filename = 'kungalv_house_prices.csv'

#write the extract data to a csv file
def write_csv(extract_data, output_filename):
    with open(output_filename, 'w', newline='') as csvfile:
        fieldnames = ['date', 'address','location', 'boarea', 'biarea', 'total_area','rooms', 'plot_area', 'closing_price']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
            



extracted_data = process_tar_file(tar_filename)
write_csv(extracted_data, output_filename)
print(f"Data saved to {output_filename}.")
