from bs4 import BeautifulSoup
import requests
import pandas as pd
import time


def main():
    #get hmtl from homepage to start building URL
    base_url = "https://finder.cstone.space/"
    base_page = requests.get(base_url) 
    soup = BeautifulSoup(base_page.text, 'html.parser')

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
    for index, endpoint in enumerate(api_endpoints):
        available_items.append(links[index] + " \n")
        response = requests.get(base_url + endpoint)
        data = response.json()
        for component in data:
            if component["Sold"] != 0:
                component_id = component["ItemId"]
                component_name = component["Name"]
                available_items.append(dict(id=component_id, name=component_name))

    #scrape hmtl from full url and add location field to items
    current_url = ""
    for item in available_items:
        if isinstance(item, str):
            current_url = item[:-2]
            continue
        else:
            current_page = requests.get(current_url + item['id']) 
            current_page_html = BeautifulSoup(current_page.text, 'html.parser')
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
            time.sleep(2)

    df = pd.DataFrame(available_items)
    df.to_csv('ShipComponents.csv', index=False)

if __name__ == "__main__":
    main()    