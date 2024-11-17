import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
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
                        location = location_parts[-2].strip()  #get the last line containing the location
                    else:
                        location = ''
                    
                    #extract Boarea, Biarea, and Rooms
                    area_elem = entry.find('div', class_='sold-property-listing__subheading sold-property-listing__area')
                    if area_elem:
                        area_text = area_elem.text.strip()
                        if area_text:
                            
                            boarea_biarea = area_text.split()
                            boarea = boarea_biarea[0]  #first part is boarea
                            biarea = boarea_biarea[2] if len(boarea_biarea) > 2 else '0'  #second part after '+' is biarea
                                
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
                    
                    #extract Tomt area
                    tomt_elem = entry.find('div', class_='sold-property-listing__land-area')
                    if tomt_elem:
                        tomt_text = tomt_elem.text.strip()
                        tomt = tomt_text.replace('tomt', '').replace('m²', '').strip()
                    else: 
                        tomt_elem= ''
                    
                    #append extracted data to the list
                    data.append([date, address, location, boarea, biarea, totalarea, rooms, tomt, price])

#define the header for the CSV file
header = ['Date', 'Address', 'Location', 'Boarea', 'Biarea', 'Totalarea', 'Rooms','Tomt_area', 'Closing_Price']

#write the extracted data to a CSV file
csv_file = 'property_data.csv'
with open(csv_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(header)  #write the header row
    writer.writerows(data)   #write the data rows

print(f"Data written to {csv_file}.")

#Problem2

#read the CSV file
df = pd.read_csv('property_data.csv')
#function to convert Swedish month names to numbers
def swedish_month_to_number(month):
    months = {
        'januari': '01', 'februari': '02', 'mars': '03', 'april': '04',
        'maj': '05', 'juni': '06', 'juli': '07', 'augusti': '08',
        'september': '09', 'oktober': '10', 'november': '11', 'december': '12'
    }
    return months.get(month.lower(), month)

#preprocess the 'Date' column
df['Date'] = df['Date'].str.replace('Såld ', '', regex=False)
df['Date'] = df['Date'].apply(lambda x: ' '.join([x.split()[0], swedish_month_to_number(x.split()[1]), x.split()[2]]))

#convert 'Date' column to datetime
df['Date'] = pd.to_datetime(df['Date'], format='%d %m %Y')

#create a copy of selected houses sold in 2022
df_2022 = df[df['Date'].dt.year == 2022].copy()

#set values
df_2022.loc[:, 'Boarea'] = pd.to_numeric(df_2022['Boarea'], errors='coerce')
df_2022.loc[:, 'Rooms'] = pd.to_numeric(df_2022['Rooms'], errors='coerce')
df_2022.loc[:, 'Closing_Price'] = pd.to_numeric(df_2022['Closing_Price'].replace(r'[^\d.]', '', regex=True))


#convert Closing_Price to numeric, removing any non-numeric characters
df_2022['Closing_Price'] = pd.to_numeric(df_2022['Closing_Price'].replace(r'[^\d.]', '', regex=True))

#convert Boarea to numeric
df_2022['Boarea'] = pd.to_numeric(df_2022['Boarea'], errors='coerce')

#convert Rooms to numeric
df_2022['Rooms'] = pd.to_numeric(df_2022['Rooms'], errors='coerce')

#compute five-number summary
summary = df_2022['Closing_Price'].describe()
print("Five-number summary of closing prices:")
print(summary[['min', '25%', '50%', '75%', 'max']])

#construct histogram of closing prices
n_bins = int(1 + 3.322 * np.log10(len(df_2022)))
plt.figure(figsize=(10, 6))
plt.hist(df_2022['Closing_Price'], bins=n_bins, edgecolor='red')
plt.title('Histogram of Closing Prices (2022)')
plt.xlabel('Closing Price')
plt.ylabel('Frequency')
plt.savefig('closing_prices_histogram.png')
plt.close()

#construct scatter plot of closing price vs boarea
plt.figure(figsize=(10, 6))
plt.scatter(df_2022['Boarea'], df_2022['Closing_Price'])
plt.title('Closing Price vs Boarea (2022)')
plt.xlabel('Boarea')
plt.ylabel('Closing Price')
plt.savefig('closing_price_vs_boarea.png')
plt.close()

#construct scatter plot with color based on number of rooms
plt.figure(figsize=(10, 6))
scatter = plt.scatter(df_2022['Boarea'], df_2022['Closing_Price'], c=df_2022['Rooms'], cmap='viridis')
plt.colorbar(scatter, label='Number of Rooms')
plt.title('Closing Price vs Boarea, Colored by Number of Rooms (2022)')
plt.xlabel('Boarea')
plt.ylabel('Closing Price')
plt.savefig('closing_price_vs_boarea_colored.png')
plt.close()

print("All plots have been saved.")
