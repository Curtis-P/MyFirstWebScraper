from bs4 import BeautifulSoup
import requests
import pandas as pd
import time
from tqdm import tqdm


def main():
    #get hmtl from homepage to start building URL
    base_url = "https://finder.cstone.space/"
    base_page = get_with_err_output(base_url)
    soup = BeautifulSoup(base_page, 'html.parser')

    #Create url segment in line with website schema
    links = [] 
    for tag in soup.find_all('a'):
        href = tag.get("href")
        if href.startswith("/Ship") and not href.startswith("/ShipShop"):
            links.append(base_url + href[1:] +"1/")
        elif href.startswith("/Jump"):
            links.append(base_url + href[1:] + "1/")
        elif href.startswith("/Fuel"):
            links.append(base_url + href[1:] + "1/")

    api_endpoints = [
        "GetSWeapons",
        "GetSTurrets",
        "GetShipBombs",
        "GetShipBombLaunchers",
        "GetMissiles",
        "GetMRacks",
        "GetCoolers",
        "GetPowers",
        "GetDrives",
        "GetJumpDrives",
        "GetShields",
        "GetShipFlightBlades",
        "GetSMinings",
        "GetSMMods",
        "GetFuelNozzles",
        "GetFuelPods",
        "GetShipSalvageHeads",
        "GetShipSalvageMods",
        "GetShipTractorBeams",
        "GetShipTowingBeams",
        "GetShipModule",
        "GetShipPaints",
    ]

    #call api_endpoints to get url slugs, store it, create component entries, and store them for later use
    available_items = []
    for index, endpoint in enumerate(tqdm(api_endpoints, desc = "Generating available ship components...")):
        available_items.append(links[index] + " \n")
        data = get_with_err_output(base_url + endpoint)
        for component in data:
            if component["Sold"] != 0:
                component_id = component["ItemId"]
                component_name = component["Name"]
                available_items.append(dict(id=component_id, name=component_name))

    #scrape hmtl from full url and add location field to items
    current_url = ""
    for item in tqdm(available_items, desc="Scraping component location data..."):
        if isinstance(item, str):
            current_url = item[:-2]
            continue
        else:
            current_page = get_with_err_output(current_url + item['id']) 
            current_page_html = BeautifulSoup(current_page, 'html.parser')
            desired_section = current_page_html.find('div', class_="pricetab")
            desired_section_rows = desired_section.find_all('tr')

            seller_locations = []
            for row in desired_section_rows:
                data_cells = row.find_all('td')
                if not data_cells:
                    continue
                cell_text = [cell.get_text(strip=True) for cell in data_cells]
                seller_locations.append(cell_text[0])
            item['locations'] = tuple(seller_locations)
            time.sleep(1)

    df = pd.DataFrame(available_items)
    df.to_csv('ShipComponents.csv', index=False)


#helper function to print our error if requests fail.
def get_with_err_output(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        if "Get" in url:
            return response.json()
        else:
            return response.text
    except requests.exceptions.HTTPError as errh:
        print("HTTP Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Connection Error:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("Something went wrong:", err)

if __name__ == "__main__":
    main()    