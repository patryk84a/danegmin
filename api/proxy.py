from http.server import BaseHTTPRequestHandler
import urllib.request
import urllib.parse
import json

class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        # Parsujemy URL, aby wyciągnąć parametr 'url'
        query_components = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        target_url = query_components.get('url', [None])[0]

        if not target_url:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Parameter "url" is missing'}).encode('utf-8'))
            return

        try:
            # Wykonujemy zapytanie do docelowego API GUS
            headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
            req = urllib.request.Request(target_url, headers=headers)
            with urllib.request.urlopen(req, timeout=20) as response:
                content = response.read()

                # Odsyłamy odpowiedź z powrotem do przeglądarki
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*') # Kluczowy nagłówek!
                self.end_headers()
                self.wfile.write(content)

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))
