import os
from flask import Flask, request, render_template_string
from dotenv import load_dotenv
import requests

# Load API key from .env
load_dotenv()
app = Flask(__name__)

HARVARD_API_KEY = os.getenv('HARVARD_API_KEY')
CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')
CLAUDE_API_URL = 'https://api.anthropic.com/v1/messages'
API_URL = 'https://api.harvardartmuseums.org/object'

TEMPLATE = '''
<!doctype html>
<html lang="en">
<head>
    <title>Artifacta</title>
    <style>
        body { font-family: Arial; margin: 50px; line-height: 1.6; }
        .interests-container { margin: 20px 0; padding: 15px; background: #f8f8f8; border-radius: 5px; }
        .interest-options { display: flex; flex-wrap: wrap; gap: 10px; }
        .interest-option { background: white; padding: 10px; border-radius: 5px; border: 1px solid #ddd; }
        img { max-width: 100%; height: auto; border-radius: 5px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
        h1, h2, h3 { color: #333; }
    </style>
</head>
<body>
    <h1>Artifacta</h1>
    <p>Powered by the Harvard Art Museums and Anthropic's Claude</p>
    <form method="POST">
        <label for="object_id">Enter Object ID:</label>
        <input type="text" name="object_id" required value="{{ object_id or '' }}">
        <input type="submit" value="{% if image_url %}Generate Ranking{% else %}Generate Ranking{% endif %}">
    </form>

    {% if image_url %}
        <h2>{{ title }} ({{ dated }})</h2>
        <p><strong>Artist:</strong> {{ artist }}<br>
           <strong>Culture:</strong> {{ culture }}<br>
           <strong>Medium:</strong> {{ medium }}</p>
        <img src="{{ image_url }}" alt="Art Image">
        <h3>Provenance</h3>
        <p>{{ provenance }}</p>
        <h3>Story</h3>
        <p style="white-space: pre-line;">{{ story }}</p>
    {% elif error %}
        <p style="color: red;">{{ error }}</p>
    {% endif %}
</body>
</html>
'''

def fetch_art_data(object_id):
    params = {
        'apikey': HARVARD_API_KEY,
        'q': f'id:{object_id}'
    }
    response = requests.get(API_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        records = data.get('records', [])
        if records:
            record = records[0]
            return {
                'image_url': record.get('primaryimageurl'),
                'title': record.get('title'),
                'artist': record['people'][0]['name'] if record.get('people') else 'Unknown',
                'dated': record.get('dated'),
                'culture': record.get('culture'),
                'medium': record.get('medium'),
                'provenance': record.get('provenance')
            }
    return None

def create_claude_prompt(art):
    base_prompt = f"""
You are an art historian and expert on the Crusades.

Here is an image of an artwork from the Harvard Art Museums: {art['image_url']}

Title: {art['title']}
Artist: {art['artist']}
Date: {art['dated']}
Culture: {art['culture']}
Medium: {art['medium']}

Provenance: {art['provenance']}

"""

    base_prompt += """
Rate this object on a scale of 1-10 in terms of its relevance to the Crusades, with 1 being least relevant and 10 being most relevant. Explain your reasoning.
"""
    return base_prompt

def call_claude(prompt):
    headers = {
        'x-api-key': CLAUDE_API_KEY,  # Changed from 'Authorization': f'Bearer {CLAUDE_API_KEY}'
        'Content-Type': 'application/json',
        'anthropic-version': '2023-06-01'
    }
    payload = {
        "model": "claude-3-opus-20240229",
        "max_tokens": 1000,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    response = requests.post(CLAUDE_API_URL, headers=headers, json=payload)

    try:
        data = response.json()
        print("Claude API Response:", data)  # For debugging

        # Claude v3 format typically returns:
        # {'content': [{'type': 'text', 'text': '...'}]}
        for part in data.get("content", []):
            if part.get("type") == "text":
                return part.get("text")
        return f"Claude API responded, but no story was returned. Raw content: {data}"
    except Exception as e:
        print("Error parsing Claude response:", e)
        return f"Error generating story: {e}"

@app.route('/', methods=['GET', 'POST'])
def index():
    image_url = error = title = artist = dated = culture = medium = provenance = story = None
    object_id = None
    interests = []

    if request.method == 'POST':
        object_id = request.form['object_id']
        interests = request.form.getlist('interests')
        
        art = fetch_art_data(object_id)
        if art and art['image_url']:
            prompt = create_claude_prompt(art)
            story = call_claude(prompt)
            image_url = art['image_url']
            title = art['title']
            artist = art['artist']
            dated = art['dated']
            culture = art['culture']
            medium = art['medium']
            provenance = art['provenance']
        else:
            error = 'Artwork not found or no image available.'

    return render_template_string(TEMPLATE, 
                                  image_url=image_url, 
                                  title=title, 
                                  artist=artist, 
                                  dated=dated,
                                  culture=culture, 
                                  medium=medium, 
                                  provenance=provenance, 
                                  story=story, 
                                  error=error,
                                  object_id=object_id,
                                  interests=interests)

if __name__ == '__main__':
    app.run(debug=True)