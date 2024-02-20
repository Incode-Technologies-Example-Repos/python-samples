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
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN")


class RoutingHandler(BaseHTTPRequestHandler):

    def initializeIncodeSession(self):
        """Initializes a new Incode session object with the appropriate headers"""
        incodeSession = IncodeSession(
            API_URL,
            API_KEY,
            flow_id = FLOW_ID,
            executive_token=ADMIN_TOKEN
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
        elif self.path.startswith("/approve"):
            self.send_data(self.approve())
        elif self.path.startswith("/auth"):
            self.send_data(self.auth_attempt_verify())
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
        # call session start with the optional redirection_url or external_customer_id of needed
        # startResponse = incodeSession.start(redirection_url='https://example.com?custom_parameter=some+value',external_customer_id='the id of the customer in your system')
        startResponse = incodeSession.start()
        return startResponse


    def omni_get_onboarding_url(self):
        """Starts a session and generates an onboarding URL"""
        incodeSession = self.initializeIncodeSession()
        # call session start with the optional redirection_url or external_customer_id of needed
        # startResponse = incodeSession.start(redirection_url='https://example.com?custom_parameter=some+value',external_customer_id='the id of the customer in your system')
        startResponse = incodeSession.start()
        onboardingUrl = incodeSession.generate_onboarding_link(clientId=CLIENT_ID)
        fullResult = startResponse
        fullResult["url"] = onboardingUrl["url"]
        return fullResult
    
    
    def webhook(self):
        """Webhook to receive onboarding status, configure it in"""
        """incode dasboard > settings > webhook > onboarding status"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        json_data = json.loads(post_data.decode('utf-8'))
        print("Received JSON data:", json_data)
        return json_data
    
    def approve(self):
        """Webhook to receive onboarding status, configure it in"""
        """incode dasboard > settings > webhook > onboarding status"""
        """This endpoint will auto-approve(create an identity) for"""
        """any sessions that PASS."""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        json_data = json.loads(post_data.decode('utf-8'))
        
        if json_data["onboardingStatus"]=="ONBOARDING_FINISHED":
            incodeSession = self.initializeIncodeSession()
            onboarding_score=incodeSession.get_scores(manualInterviewId=json_data["interviewId"])
            if onboarding_score["overall"]["status"]=="OK":
                identity_data=incodeSession.process_approve(manualInterviewId=json_data["interviewId"])
                response = {
                    "success":True,
                    "data": identity_data
                }
                # This would return something like this:
                # {
                #   success: true,
                #   data: {
                #     success: true,
                #     uuid: '6595c84ce69d469f69ad39fb',
                #     token: 'eyJhbGciOiJ4UzI1NiJ9.eyJleHRlcm5hbFVzZXJJZCI6IjY1OTVjODRjZTY5ZDk2OWY2OWF33kMjlmYiIsInJvbGUiOiJBQ0NFU5MiLCJrZXlSZWYiOiI2MmZlNjQ3ZTJjODJlOTVhZDNhZTRjMzkiLCJleHAiOjE3MTIxOTExMDksImlhdCI6MTcwNDMyODcwOX0.fbhlcTQrp-h-spgxKU2J7wpEBN4I4iOYG5CBwuQKPLQ72',
                #     totalScore: 'OK',
                #     existingCustomer: false
                #   }
                # }
                # UUID: You can save the generated uuid of your user to link your user with our systems.
                # Token: Is long lived and could be used to do calls in the name of the user if needed.
                # Existing Customer: Will return true in case the user was already in the database, in such case we are returning the UUID of the already existing user.
                
                return response
            else:
                response = {
                    "success": False,
                    "error": "Session didn't PASS, identity was not created",
                }
                return response
        else:
            print("Received JSON data:", json_data)
            return json_data
    
    def auth_attempt_verify(self):
        """Verify auth attempt"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        json_data = json.loads(post_data.decode('utf-8'))
        incodeSession = self.initializeIncodeSession()
        authResponse = incodeSession.auth_attempt_verify(json_data['transactionId'],json_data['token'],json_data['interviewToken'])
        return authResponse


logging.basicConfig(level=logging.INFO)
server = HTTPServer(("localhost", int(3000)), RoutingHandler)
server.serve_forever()
