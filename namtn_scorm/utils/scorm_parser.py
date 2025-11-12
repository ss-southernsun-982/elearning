import zipfile
import xml.etree.ElementTree as ET
import re
import base64
import json

pattern = r'deserialize\("([^"]+)"\)'

def parse_scorm_manifest(zip_path):
    """Extract SCORM manifest and return title and chapters"""
    with zipfile.ZipFile(zip_path, 'r') as zf:
        if 'imsmanifest.xml' not in zf.namelist():
            raise ValueError("Missing imsmanifest.xml")

        manifest = zf.read('imsmanifest.xml')
        root = ET.fromstring(manifest)

        # Support namespace
        namespaces = {
            'imscp': 'http://www.imsproject.org/xsd/imscp_rootv1p1p2',
            'adlcp': 'http://www.adlnet.org/xsd/adlcp_rootv1p2'
        }

        titles = root.findall('.//imscp:title', namespaces)
        title = ''
        for title_elem in titles:
            title = title_elem.text
            break

        chapters = []
        index_html = (zf.read('scormcontent/index.html') or (zf.read('content/index.html'))).decode()
        match = re.search(r'deserialize\("([^"]+)"\)', index_html)
        if match:
            base64_data = match.group(1)
            decoded = base64.b64decode(base64_data).decode('utf-8')
            data = json.loads(decoded)
            for d in data['course']['lessons']:
                chapters.append({
                    'identifier': d['id'],
                    'title': d['title'],
                    'href': '#/lessons/%s' % d['id'],
                    'type': d['type']
                })
        return title, chapters