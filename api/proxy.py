from http.server import BaseHTTPRequestHandler
import urllib.request
import urllib.parse
import ssl
import json

class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        # Parsujemy URL, aby wyciągnąć parametr 'url'
        query_components = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        unit_id = query_components.get('unit-id', [None])[0]
        var_ids_str = query_components.get('var-ids', [None])[0]
        year_range = query_components.get('year', ["2010-2025"])[0]

        if not unit_id or not var_ids_str:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': 'Parameters "unit-id" and "var-ids" are required'}).encode('utf-8'))
            return

        try:
             # Używamy poprawnej metody API: /data/by-unit/{unit-id}
            base_url = f"https://bdl.stat.gov.pl/api/v1/data/by-unit/{unit_id}"
            
            params = {
                "var-id": var_ids_str.split(','),
                "year": year_range,
                "format": "json",
                "page-size": 100
            }
            query_string = urllib.parse.urlencode(params, doseq=True)
            full_url = f"{base_url}?{query_string}"

            # Wykonujemy zapytanie do GUS
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

            headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
            req = urllib.request.Request(full_url, headers=headers)
            with urllib.request.urlopen(req, context=ctx, timeout=30) as response:
                content = response.read()

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(content)

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))

