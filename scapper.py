from flask import Flask, jsonify, redirect
import requests
import json

app = Flask(__name__)

@app.route('/')
def redirect_to_get_time_stories():
    return redirect('/getTimeStories', code=302)

@app.route('/getTimeStories', methods=['GET'])
def get_time_stories():
    latest_stories = fetch_latest_stories()
    
    if latest_stories:
        formatted_output = '\n'.join(json.dumps(story, indent=2, ensure_ascii=False) + ',' for story in latest_stories)
        return '[\n' + formatted_output.rstrip(',') + '\n]'
    else:
        return jsonify({'error': 'Failed to fetch latest stories'}), 500

def fetch_latest_stories():
    # Fetch HTML content from the Time.com website
    url = "https://time.com"
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code == 200:
        html_content = response.text
        
        start_marker = '<li class="most-popular-feed__item">'
        end_marker = '</li>'
        
        latest_stories = []
        index = 0
        while index < 6:
            start_index = html_content.find(start_marker)
            end_index = html_content.find(end_marker, start_index)
            
            if start_index == -1 or end_index == -1:
                break
            
            story_text = html_content[start_index:end_index + len(end_marker)]
            latest_stories.append(parse_story(story_text))
            
            # Remove processed portion from html_content
            html_content = html_content[end_index + len(end_marker):]
            
            index += 1
        
        return latest_stories
    else:
        print(f"Failed to fetch content. Status code: {response.status_code}")
        return None

def parse_story(story_text):
    # Extract information from a story using basic string manipulation
    section_start = story_text.find('<a class="most-popular-feed__item-section"')
    section_end = story_text.find('</a>', section_start)
    section = story_text[section_start + len('<a class="most-popular-feed__item-section"'):section_end].strip()

    headline_start = story_text.find('<h3 class="most-popular-feed__item-headline">')
    headline_end = story_text.find('</h3>', headline_start)
    headline = story_text[headline_start + len('<h3 class="most-popular-feed__item-headline">'):headline_end].strip()

    link_start = story_text.find('<a href="')
    link_end = story_text.find('"', link_start + len('<a href="'))
    link = story_text[link_start + len('<a href="'):link_end]

    return {
        'title': headline,
        'link': link,
    }

if __name__ == '__main__':
    app.run(host='localhost', port=5000)
