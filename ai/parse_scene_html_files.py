import re
import json
from bs4 import BeautifulSoup
from tqdm import tqdm

import requests
from bs4 import BeautifulSoup

def download_and_save_script(url, output_file_path):
    # Send a GET request to the URL
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse HTML content with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the <td> tag with class 'scrtext' and get the content of the <pre> tag
        td_tag = soup.find('td', class_='scrtext')

        if td_tag:
            pre_tag = td_tag.find('pre')

            if pre_tag:
                # Extract text content from the <pre> tag
                script_text = pre_tag.get_text()

                # Save script content to a text file
                with open(output_file_path, 'w', encoding='utf-8') as output_file:
                    output_file.write(script_text)
                print(f'Script downloaded and saved to: {output_file_path}')
            else:
                print('Error: Script content not found in the HTML structure.')
        else:
            print('Error: Unable to find the script element on the page.')
    else:
        print(f'Error: Failed to retrieve the page. Status code: {response.status_code}')


import re
import json

def parse_script_scenes(file_path):
    with open(file_path, 'r') as file:
        script_content = file.read()

    # Define regular expression for scene heading
    scene_heading_pattern = re.compile(r'^\s*(EXT\.|INT\.|)')


    # Split script into scenes based on the presence of a scene heading
    scenes = re.split(scene_heading_pattern, script_content)[1:]

    # Parse each scene and tag lines
    parsed_script = []
    for i in range(0, len(scenes), 2):  # Iterate every two elements (scene heading + scene content)
        scene_heading = scenes[i].strip()
        scene_content = scenes[i + 1].strip()

        # Extract lines from the scene content
        lines = scene_content.split('\n')

        # Parse lines and tag elements
        parsed_lines = []
        for line in lines:
            # Exclude empty lines
            if line.strip():
                parsed_lines.append(line)

        parsed_script.append({"scene_heading": scene_heading, "scene_content": parsed_lines})

    return parsed_script


# Example usage:
file_path = './Joker.txt'
parsed_script = parse_script_scenes(file_path)

print(len(parsed_script))
# Print the result
# print(json.dumps(parsed_script[:2], indent=2))

# Example usage:
# url = 'https://www.imsdb.com/scripts/Joker.html'
# output_file_path = './Joker.txt'
# download_and_save_script(url, output_file_path)
