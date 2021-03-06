import requests
import DSR_Equipment as dsr
from os import path, mkdir
from bs4 import BeautifulSoup as soup

# Imports for exception handling.
from socket import gaierror
from urllib3.exceptions import NewConnectionError, MaxRetryError
from requests.exceptions import ConnectionError
from contextlib import suppress


class GetImageFile:

    def __init__(self, folder, url, url_path):
        """
        :param folder: Folder for storing downloaded image files.
        :param url: Homepage for website.
        :param url_path: URL path mainly used for concatenation with url param.
        This is used for downloading image from source
        """
        self.folder = folder
        self.url = url
        self.url_path = url_path
        self.file_name = self.url_path.rsplit('/', 1)[1]

    def __repr__(self):
        return f"GetImageFile({self.folder}, {self.url_path}, {self.url})"

    def download_content(self):
        try:
            # Download and write images to folder.
            with open(f"{self.folder}/{self.file_name}", 'wb') as f:
                print(f"Downloading {self.file_name}...")
                f.write(requests.get(self.url + self.url_path).content)
                print(f"Downloaded {self.file_name} successful!")
        except (gaierror, NewConnectionError, MaxRetryError, ConnectionError):
            print(f"Error! Attempting to download from {self.url_path}...")
            self.download_from_img_src()

    def download_from_img_src(self):
        """Try to download image from 'self.url_path' without concatenating 'self.site'.
        If it fails, skip download regardless of any exception."""
        try:
            with open(f"{self.folder}/{self.file_name}", 'wb') as f:
                print(f"Downloading {self.file_name}...")
                f.write(requests.get(self.url_path).content)
                print(f"Downloaded {self.file_name} successful!")
        except:
            print(f"Failed to download {self.file_name}. Skipping download.")


class PrepIMGFiles:

    def __init__(self, category, folder_name, tag):
        """
        :param category: URL values from 'dsr_equipment' used to create BeautifulSoup objects.
        :param folder_name: Folder name for storing downloaded image files.
        :param tag: HTML tag which contains <img src=...>.
        """
        self.category = category
        self.folder_name = folder_name
        self.tag = tag

    def __repr__(self):
        return f"PrepIMGFiles({self.category}, {self.folder_name}, {self.tag})"

    def find_img_src(self):
        """Create BeautifulSoup objects with URLs and parse through them until <img src=...> tag is found."""
        print(f'\nFetching data for {self.folder_name}...')
        data = [soup(requests.get(value).text, 'html.parser') for value in self.category.values()]

        self.create_folder_for_content()

        print('Fetching images from data...\n')
        for items in data:
            try:
                for _tag in items.find_all(self.tag):
                    with suppress(AttributeError, TypeError):
                        GetImageFile(self.folder_name, dsr_page, _tag.a.img['src']).download_content()
            except KeyError:
                for _tag in items.find_all(*self.tag):
                    with suppress(AttributeError, TypeError):
                        GetImageFile(self.folder_name, dsr_page, _tag.a.img['src']).download_content()
        print('Downloads for spells complete!')

    def create_folder_for_content(self):
        """Creates a folder for storing downloaded images."""
        if path.isdir(self.folder_name) is False:
            print('Creating directory for images...')
            mkdir(self.folder_name)


def main():
    equipment_categories = [
        PrepIMGFiles(dsr.spells, 'Spells', 'tr'),
        PrepIMGFiles(dsr.weapons, 'Weapons', 'tr'),
        PrepIMGFiles(dsr.shields, 'shields', ('div', {'class': 'col-sm-2'})),
        PrepIMGFiles(dsr.armor, 'Armor', 'tr'),
        PrepIMGFiles(dsr.rings, 'Rings', 'tr'),
        PrepIMGFiles(dsr.items, 'Items', 'tr')
    ]

    # Set format string for 'user_input' based on the number of objects in 'equipment_categories'.
    options_fmt = '\n|{:^50}|' * (len(equipment_categories) + 2)
    fmt = f"\n+{'-' * 50}+{options_fmt}\n+{'-' * 50}+\nChoose Option: "

    while True:
        user_input = input(fmt.format(
            '1. Download Spell Images ',
            '2. Download Weapon Images',
            '3. Download Shield Images',
            '4. Download Armor Images ',
            '5. Download Ring Images  ',
            '6. Download Item Images  ',
            '7. Download All Images   ',
            '8. Exit                  '
        ))

        # Gives all objects in 'equipment_categories' an index to choose from for 'user_input'.
        for index, equipment in enumerate(equipment_categories, 1):
            if user_input == str(index):
                equipment.find_img_src(); break

        # Download all images.
        if user_input == str(len(equipment_categories) + 1):
            for equipment in equipment_categories:
                equipment.find_img_src()

        # Exits the program.
        if user_input == str(len(equipment_categories) + 2):
            raise SystemExit

        # Print error if an invalid input is entered.
        if user_input not in [str(num + 1) for num in range(len(equipment_categories) + 2)]:
            print(f"Invalid input. Please enter a digit from 1-{len(equipment_categories) + 2}.")


dsr_page = 'https://darksouls.wiki.fextralife.com'

if __name__ == '__main__':
    main()
