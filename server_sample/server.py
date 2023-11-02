from http.server import HTTPServer, BaseHTTPRequestHandler
import logging, ngrok, os
from Session import Session as IncodeSession
from dotenv import load_dotenv
load_dotenv("sample.env") # Update path to .env once you fill in the environment details and change the filename to .env

API_URL = os.getenv("API_URL")
API_VERSION = os.getenv("API_VERSION")
API_KEY = os.getenv("API_KEY")
CLIENT_ID = os.getenv("CLIENT_ID")
FLOW_ID = os.getenv("FLOW_ID")
HTTP_PORT = os.getenv("HTTP_PORT")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL") # Optional
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD") # Optional
SELFIE_PATH = os.getenv("SELFIE_PATH") # Optional
FRONT_ID_PATH = os.getenv("FRONT_ID_PATH") # Optional
BACK_ID_PATH = os.getenv("BACK_ID_PATH") # Optional

# Not necessary for this vanilla implementation, but if you add an endpoint that requires the admin credentials, the format is illustrated here. 
ADMIN_CREDENTIALS = {  # Optional
    "email": ADMIN_EMAIL,
    "password" : ADMIN_PASSWORD
}

# Not necessary for this vanilla implementation, but if you add an endpoint that requires documents, the format is illustrated here. 
DOCUMENTS = {  # Optional
    "selfie": SELFIE_PATH,
    "front_id": FRONT_ID_PATH,
    "back_id": BACK_ID_PATH
}


class RoutingHandler(BaseHTTPRequestHandler):

    def initializeIncodeSession(self):
        """Initializes a new Incode session object with the appropriate headers"""
        incodeSession = IncodeSession(
            API_URL,
            API_KEY,
            documents = DOCUMENTS,
            flow_id = FLOW_ID,
            admin_credentials = ADMIN_CREDENTIALS,
        )
        return incodeSession
    

    def do_GET(self):
        if self.path == "/start":
            self.send_data(self.omni_start())
        if self.path == "/onboarding-url":
            self.send_data(self.omni_get_onboarding_url())
        if self.path == "/onboarding-url-without-api-key":
            self.send_data(self.omni_get_onboarding_url_without_api_key())
        if self.path == "/executive-token":
            if ADMIN_EMAIL != 'None' and ADMIN_PASSWORD != 'None' and ADMIN_EMAIL and ADMIN_PASSWORD:
                self.send_data(self.omni_get_executive_token())
            else:
                self.send_data("Please make sure you added your admin email and password to the environment variables.")
        else:
            self.send_data("Hello, this route does not exist :-)")


    def send_data(self, msg):
        """Sends the data"""
        body = bytes(str(msg), "utf-8")
        self.protocol_version = "HTTP/1.1"
        self.send_response(200)
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)
        

    def omni_start(self):
        """Starts a new session"""
        incodeSession = self.initializeIncodeSession()
        startResponse = incodeSession.start()
        return startResponse
    

    def omni_get_onboarding_url(self):
        """Starts a session and generates an onboarding URL"""
        incodeSession = self.initializeIncodeSession()
        startResponse = incodeSession.start()
        onboardingUrl = incodeSession.generate_onboarding_link(clientId=CLIENT_ID)
        fullResult = {
            "startResponse" : startResponse,
            "onboardingUrl" : onboardingUrl
        }
        return fullResult
    

    def omni_get_onboarding_url_without_api_key(self):
        """This demonstrates how you can securely interpolate the token returned by omni/start with /0, to exclude the API key from future API calls"""
        incodeSession = self.initializeIncodeSession()
        startResponse = incodeSession.start()
        incodeSession.s.headers.__delitem__("x-api-key") # Deleting the API key from the headers and only including the token in the header
        r = incodeSession.s.get(f"{incodeSession.base_url}0/omni/onboarding-url?clientId={CLIENT_ID}") # Using /0/ in the route to indicate that there is no API key and the token should be used for authentication
        response = r.json()
        incodeSession.api_call_dict["generate_onboarding_link"] = r.request
        fullResult = {
            "startResponse" : startResponse,
            "onboardingUrl" : response
        }
        return fullResult
    

    def omni_get_executive_token(self):
        """Creates an executive token. You will use this for operations that don't require a new session. For example: sending an onboarding URL to a customer via our SMS endpoint."""
        incodeSession = self.initializeIncodeSession()
        executiveToken = incodeSession.fetchExecutiveToken()
        return executiveToken
    

logging.basicConfig(level=logging.INFO)
server = HTTPServer(("localhost", int(HTTP_PORT)), RoutingHandler)
listener = ngrok.connect(f"localhost:{HTTP_PORT}", authtoken_from_env=True)
server.serve_forever()