from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import os
import zipfile
from io import BytesIO
from urllib.parse import urljoin, urlparse

app = Flask(__name__)
CORS(app)

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def download_website(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        base_url = url
        website_content = {
            'html': str(soup),
            'assets': {}
        }

        asset_tags = {
            'img': 'src',
            'link': 'href',
            'script': 'src'
        }

        for tag, attr in asset_tags.items():
            for element in soup.find_all(tag):
                asset_url = element.get(attr)
                if asset_url:
                    if not asset_url.startswith("http"):
                      asset_url = urljoin(base_url, asset_url)

                    if is_valid_url(asset_url):
                      try:
                            asset_response = requests.get(asset_url, timeout=5)
                            asset_response.raise_for_status()
                            
                            relative_path = urlparse(asset_url).path.lstrip('/')
                            website_content['assets'][relative_path] = asset_response.content
                      except requests.exceptions.RequestException:
                         pass
        return website_content
    except requests.exceptions.RequestException as e:
        return None, str(e)

def create_zip(website_content):
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.writestr('index.html', website_content['html'])
        for path, content in website_content['assets'].items():
            zipf.writestr(path, content)
    zip_buffer.seek(0)
    return zip_buffer

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    url = data.get('url')

    if not url:
        return jsonify({'error': 'URL is required'}), 400
    if not is_valid_url(url):
        return jsonify({'error': 'invalid URL'}), 400
    
    website_content, error = download_website(url)
    if error:
         return jsonify({'error': f'Failed to download website: {error}'}), 500

    if not website_content:
         return jsonify({'error': "Failed to download website"}), 500

    zip_file = create_zip(website_content)
    return send_file(zip_file, as_attachment=True, download_name='website-code.zip',mimetype='application/zip')

if __name__ == '__main__':
    app.run(debug=True, port=5000)