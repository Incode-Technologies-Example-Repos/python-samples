from http.server import HTTPServer, BaseHTTPRequestHandler
import logging, os
import json
from Session import Session as IncodeSession
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qs

load_dotenv(".env")

API_URL = os.getenv("API_URL")
API_KEY = os.getenv("API_KEY")
CLIENT_ID = os.getenv("CLIENT_ID")
FLOW_ID = os.getenv("FLOW_ID")


class RoutingHandler(BaseHTTPRequestHandler):

    def initializeIncodeSession(self):
        """Initializes a new Incode session object with the appropriate headers"""
        incodeSession = IncodeSession(
            API_URL,
            API_KEY,
            flow_id = FLOW_ID
        )
        return incodeSession
    

    def do_GET(self):
        if self.path.startswith("/start"):
            self.send_data(self.omni_start())
        elif self.path.startswith("/onboarding-url"):
            self.send_data(self.omni_get_onboarding_url())
        else:
            self.send_error(404, "Cannot GET " + self.path)

    def do_POST(self):
        if self.path.startswith("/webhook"):
            self.send_data(self.webhook())
        else:
            self.send_error(404, "Cannot POST " + self.path)

    def do_OPTIONS(self):
        self.do_GET()


    def send_data(self, msg):
        """Sends json data"""
        body = json.dumps(msg).encode('utf-8')
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept, Authorization, ngrok-skip-browser-warning")
        self.send_header("Access-Control-Allow-Credentials", "true")
        super().end_headers()
        self.wfile.write(body)
    
    def send_error(self, http_status, msg):
        """Sends error response"""
        self.send_response(http_status)
        self.send_header("Content-Type", "application/json")
        super().end_headers()
        response = json.dumps({'error': msg})
        self.wfile.write(response.encode('utf-8'))


    def omni_start(self):
        """Starts a new session"""
        incodeSession = self.initializeIncodeSession()
        startResponse = incodeSession.start()
        return startResponse


    def omni_get_onboarding_url(self):
        """Starts a session and generates an onboarding URL"""
        query_components = parse_qs(urlparse(self.path).query)
        redirection_url = query_components.get('redirectionUrl', [''])[0]
        incodeSession = self.initializeIncodeSession()
        startResponse = incodeSession.start(redirection_url)
        onboardingUrl = incodeSession.generate_onboarding_link(clientId=CLIENT_ID)
        fullResult = startResponse
        fullResult["url"] = onboardingUrl["url"]
        return fullResult
    
    
    def webhook(self):
        """Starts a session and generates an onboarding URL"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        json_data = json.loads(post_data.decode('utf-8'))
        print("Received JSON data:", json_data)
        return json_data


logging.basicConfig(level=logging.INFO)
server = HTTPServer(("localhost", int(3000)), RoutingHandler)
server.serve_forever()
