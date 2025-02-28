import requests
from bs4 import BeautifulSoup
import csv
import sys
import os
import re
from urllib.parse import urlparse

def remove_numbers_in_parentheses(text):
    # Regular expression to match numbers in parentheses (including decimal numbers)
    return re.sub(r'\(\s*\d+(\.\d+)?\s*\)', '', text)

# Function to extract the first date found on the webpage (in format: "Mon dd, yyyy")
def extract_date_from_page(content):
    # Regular expression pattern for a date like "Apr 23, 2019"
    # date_pattern = r'\b([A-Za-z]{3})[\s\d\.\-]*?(\d{1,2}),\s*(\d{4})\b'
    date_pattern = r'\b([A-Za-z]{3,4})\..*?(\d{1,2}),\s*(\d{4})\b'
    match = re.search(date_pattern, content)
    # print(f"date: {match.group(2)} {match.group(1)} {match.group(3)}")

    if match:
        # Return the date in the format "Mon dd, yyyy"
        # return match.group(0)
        return f"{match.group(2)} {match.group(1)} {match.group(3)}"

    return None


def scrape_table_to_csv(url):
    # Send an HTTP request to the website
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"Failed to retrieve the webpage: {url}")
        return
    

    # Extract the page content (HTML) to search for a date
    page_content = response.text
    
    # Extract date from the page content
    page_date = extract_date_from_page(page_content)
    
    if page_date:
        print(f"Found date: {page_date}")
    else:
        print(f"No date found on the page: {url}")
        page_date = "Unknown Date"


    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find the first table in the webpage
    table = soup.find('table')
    
    if not table:
        print(f"No table found on the webpage: {url}")
        return
    
    # Extract table headers (if any)
    # headers = ["Rank","School","Music Ind","Music Ens","Music Avg","Visual Ind","Visual Ens","Visual Avg","General Mus 1","General Mus 2","General Mus Total","General Vis","General Effect Total","Total","Class Rank","Panel Rank","Date"]
    headers = ["date","rank","school","music_individual","music_ensemble","music_average","visual_individual","visual_ensemble","visual_average","general_music_1","general_music_2","general_music_total","general_visual","general_effect_total","total","class_rank","panel_rank"]
    # header_row = table.find('tr')
    # if header_row:
    #     header_cells = header_row.find_all(['th', 'td'])
    #     headers = [cell.get_text(strip=True) for cell in header_cells]
    
    # Extract table rows
    # rows = table.find_all('tr')[1:]  # Skip the header row
    rows = table.find('tbody').find_all('tr')  # Skip the header row
    
    table_data = []
    
    for row in rows:
        cells = row.find_all('td')
        # row_data = [cell.get_text(strip=True) for cell in cells]
        row_data = [remove_numbers_in_parentheses(cell.get_text(strip=True)) for cell in cells]
        row_data.insert(0,page_date)


        # row_data = [remove_numbers_in_parentheses(cell.get_text(strip=True)) for cell in cells]
        # row_data.append(page_date)
        table_data.append(row_data)
    
    # Generate a filename based on the URL's HTML file name
    parsed_url = urlparse(url)
    filename = os.path.basename(parsed_url.path)
    
    # If there's no file in the URL (e.g., just a directory), use 'output.csv'
    if not filename or filename == '/':
        filename = 'output.html'

    # Remove any query parameters or fragments from the filename
    filename = filename.split('?')[0].split('#')[0]

    # Change the file extension to CSV
    csv_filename = f"{filename}.csv"

    # Write the data to the CSV file
    with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file,quoting=csv.QUOTE_ALL)
        
        # Write headers first (if any)
        if headers:
            writer.writerow(headers)
        
        # Write table rows
        writer.writerows(table_data)
    
    print(f"Data has been written to {csv_filename} from {url}")

# Read URLs from standard input (stdin)
def read_urls_from_stdin():
    urls = sys.stdin.read().splitlines()
    return urls

# Main function to process each URL
def main():
    urls = read_urls_from_stdin()
    
    if not urls:
        print("No URLs provided.")
        return

    for url in urls:
        scrape_table_to_csv(url)

# Run the script
if __name__ == "__main__":
    main()
