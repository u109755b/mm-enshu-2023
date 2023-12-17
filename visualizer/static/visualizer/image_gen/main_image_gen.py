import os
import json
import re
import subprocess
import time
import argparse

def make_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)  # Use makedirs to create intermediate directories
        
def sanitize_directory_name(name):
    """Sanitize the directory name by replacing or removing invalid characters."""
    # Replace spaces with underscores and remove other non-alphanumeric characters
    return re.sub(r'[^a-zA-Z0-9_]', '', name.replace(' ', '_'))
        
def process_data(data, section_name=None, novel_title=None, log_csv_path=None, api_key_path=None, image_save_dir=None):
    image_count = 0  # Initialize a counter for successful image generations
    for item in data:
        current_section_name = item.get("sectionName", section_name)

        if "subSection" in item:
            image_count += process_data(item["subSection"], current_section_name, novel_title, log_csv_path, api_key_path, image_save_dir)
        elif "nodes" in item and current_section_name:
            chapter_dir = os.path.join(image_save_dir, sanitize_directory_name(current_section_name))
            make_dir(chapter_dir)
            for node in item["nodes"]:
                if print_node_info(node, chapter_dir, novel_title, log_csv_path, api_key_path):
                    node['image'] = os.path.join(sanitize_directory_name(current_section_name), sanitize_directory_name(node['label']) + '.png')
                    node['shape'] = 'image'
                    image_count += 1
    return image_count


def print_node_info(node, chapter_dir, novel_name, log_csv_path, api_key_path):
    image_path = os.path.join(chapter_dir, sanitize_directory_name(node['label']) + '.png')
    character_name = node['label']
    character_description = node['title']

    # Call get_image.py script with necessary arguments
    result = subprocess.run([
        'python3', 'get_image.py', 
        '--novel_name', novel_name, 
        '--character_name', character_name, 
        '--character_description', character_description, 
        '--image_save_path', image_path, 
        '--log_file_path', log_csv_path,
        '--api_key_file_path', api_key_path
    ], capture_output=True)

    return result.returncode == 0  # Return True if image generation was successful
    
def main(gutenberg_id, api_key_file_path):
    novels_base_dir = '../summarized_data/'
    target_novel_dir = novels_base_dir + str(gutenberg_id) + '/sample0/'
    summarized_json_path = target_novel_dir + 'all_data.json'
    image_save_dir = target_novel_dir + 'images/'
    image_gen_log_csv_path = target_novel_dir + 'image_gen_log.csv'
    image_gen_log_for_all_novels = './ImGen_execution.csv'

    make_dir(image_save_dir)

    with open(target_novel_dir + 'title.txt', 'r') as f:
        title = f.read()
    print(title)

    with open(summarized_json_path, 'r') as f:
        data = json.load(f)

    start = time.time()
    image_count = process_data(data, novel_title=title, log_csv_path=image_gen_log_csv_path, api_key_path=api_key_file_path, image_save_dir=image_save_dir)
    end = time.time()

    with open(summarized_json_path, 'w') as f:
        json.dump(data, f, indent=4)

    with open(image_gen_log_for_all_novels, 'a') as f:
        f.write(f"{title},{end - start},{image_count}\n")
        
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate images for a novel.')
    parser.add_argument('--gutenberg_id', type=int, help='The Gutenberg ID of the novel.', default=0)
    parser.add_argument('--api_key_file_path', type=str, help='The path to the API key file.', default='./api_key.txt')
    
    args = parser.parse_args()
    main(args.gutenberg_id, args.api_key_file_path)