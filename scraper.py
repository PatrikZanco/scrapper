import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from playwright.sync_api import sync_playwright
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

 
DEBUG = True
def get_all_percentages_from_page(url) -> list:
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto(url)
            page.wait_for_selector(
                'span.common-flucs-graph__percentage', state='visible')
            html = page.content()
            soup = BeautifulSoup(html, 'html.parser')
            percentage_tags = soup.find_all(
                'span', class_='common-flucs-graph__percentage')
            percentages = [tag.text.strip() for tag in percentage_tags]
            return percentages
    except Exception as e:
        print(f"An error occurred: {e}")
        return []


def get_all_opens_from_page(url) -> list:
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto(url)
            page.wait_for_load_state('load')
            html = page.content()
            soup = BeautifulSoup(html, 'html.parser')
            for tag in soup.find_all('tr', attrs={'data-v-7151d989': True}):
                tag.decompose()
            divs = soup.find_all(
                'div', class_='form-guide-overview-insight-card__content-item')

            open_values = []

            for div in divs:
                print(div)
                spans = div.find_all('span')
                if spans and spans[0].text.strip() == "Open":
                    open_values.append(spans[1].text.strip())

            return open_values
    except Exception as e:
        print(f"An error occurred: {e}")
        return []


def scrape_race_info():
    # URL of the race
    url = "https://www.punters.com.au/form-guide/horses/bendigo-20241203/apiam-animal-health-mdn-plate-race-1/"
    driver = webdriver.Chrome()
    driver = driver.get(url=url)

    try:

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # No inicio da loop uma linha e pulada por cause do header da tabela
        percentages = get_all_percentages_from_page(url)
        open_val = get_all_opens_from_page(url)

        if DEBUG:
            print(percentages)
            print(open_val)

        # Dictionary to store all page information
        page_data = {
            'page_title': soup.title.text if soup.title else '',
            'header_info': {},
            'main_content': {},
            'race_details': {},
            'horse_information': [],
            'additional_info': {},
            'raw_text': []
        }

        # Get all header information
        header = soup.find('header')
        if header:
            page_data['header_info'] = {
                'text': header.get_text(separator=' | ', strip=True),
                'navigation': [link.text.strip() for link in header.find_all('a') if link.text.strip()]
            }

        # Get main content area
        main_content = soup.find('main')
        if main_content:
            # Race name and details
            race_name = main_content.find('h1')
            if race_name:
                page_data['main_content']['race_name'] = race_name.text.strip()

            # Race details
            race_details = main_content.find_all(
                ['div', 'p'], class_=lambda x: x and 'race' in x.lower())
            page_data['race_details'] = {
                'details': [detail.get_text(strip=True) for detail in race_details if detail.get_text(strip=True)]
            }

            # Horse information table
            horse_table = main_content.find('table')

            if horse_table:
                headers = []
                header_row = horse_table.find('tr')
                if header_row:
                    headers = [th.get_text(strip=True)
                               for th in header_row.find_all(['th', 'td'])]

                # As porcentagems estao na ordem que aparecem
                counter = 0

                table = horse_table.find_all('tr')[1:]
                table = [table[i] for i in range(len(table)) if i % 2 == 0]

                for row in table:  # Skip header row

                    print(type(horse_table.find_all('tr')))

                    horse_data = {}
                    cells = row.find_all(['td', 'th'])

                    for i, cell in enumerate(cells):
                        # Captura do percentual
                        flucs_element = cell.select(
                            'span.common-flucs-graph__percentage')
                        if flucs_element:
                            flucs_element = cell.select_one(
                                'span.common-flucs-graph__percentage').replace('%', '')
                            return int(flucs_element)

                        # Captura do valor de Open
                        try:
                            button = driver.find_element(
                                By.CSS_SELECTOR, "button.form-guide-overview-selection__toggle-button")
                            button = button.click()

                            open_element = cell.select_one(
                                'div.form-guide-overview-insight-card__content-item')
                            if open_element:
                                spans = open_element.find_all('span')
                                if len(spans) > 1 and spans[0].text.strip() == "Open":
                                    horse_data['Open'] = spans[1].text.strip()

                        except Exception as e:
                            return f'Error: {e}'

                        # Captura de Odds
                        odds_element = cell.select_one(
                            '.form-guide-overview-selection__odds')
                        if odds_element:
                            horse_data['Odds'] = odds_element.text.strip()

                        # Captura do Rating
                        # Ajuste o seletor para o correto
                        rating_element = cell.select_one(
                            '.some-class-for-rating')
                        if rating_element:
                            horse_data['Rating'] = rating_element.text.strip()

                        # Verificação de dados capturados
                        print(horse_data)

                        # Get all text content including nested elements
                        cell_content = cell.get_text(
                            separator=' | ', strip=True)
                        if i < len(headers):
                            horse_data[headers[i]
                                       if headers else f'column_{i}'] = cell_content
                        else:
                            horse_data[f'additional_column_{i}'] = cell_content

                        # Get any links in the cell
                        links = cell.find_all('a')
                        if links:
                            horse_data[f'links_{i}'] = [
                                {'text': a.text.strip(), 'href': a.get('href', '')} for a in links]

                    # contador para porcentagens
                    counter = counter + 1

                    if horse_data:
                        page_data['horse_information'].append(horse_data)

        # Get all text content from the page
        for text in soup.stripped_strings:
            if text.strip():
                page_data['raw_text'].append(text.strip())

        # Get any additional information sections
        info_sections = soup.find_all(['section', 'div'], class_=True)
        for section in info_sections:
            section_name = section.get('class', ['unknown_section'])[0]
            section_content = section.get_text(separator=' | ', strip=True)
            if section_content:
                page_data['additional_info'][section_name] = section_content

        # Save to JSON file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'race_data_{timestamp}.json'

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(page_data, f, indent=4, ensure_ascii=False)

        print(
            f"Complete page data successfully scraped and saved to {filename}")
        return page_data

    except requests.RequestException as e:
        print(f"Error fetching the webpage: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


if __name__ == "__main__":
    scrape_race_info()
