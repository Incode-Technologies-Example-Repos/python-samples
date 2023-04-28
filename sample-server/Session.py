import requests

########################
# INCODE SESSION CLASS #
########################

class Session:

    def __init__(self, base_url, api_key, flow_id) -> None:
        self.base_url = base_url
        self.api_key = api_key
        self.flow_id = flow_id
        self.interview_id = ""
        self.session = requests.Session()
        self.session.stream = False
        self.session.headers.update({"x-api-key": self.api_key, "api-version": "1.0"})

    def start(self, redirection_url = None):
        """https://docs.incode.com/docs/omni-api/api/onboarding#start-onboarding"""
        
        params = {"countryCode": "ALL", "configurationId": self.flow_id, "language": "en-US"}

        if redirection_url:
            params['redirectionUrl'] = redirection_url
        
        r = self.session.post(
            self.base_url + "/omni/start",
            json=params,
        )
        resp = r.json()
        self.interview_id = resp["interviewId"]
        self.client_id = resp["clientId"]
        self.session.headers.update(
            {
                "X-Incode-Hardware-Id": resp["token"],
                "api-version": "1.0",
                "Content-type": "application/json",
            }
        )
        return {"token": resp["token"], "interviewId": resp["interviewId"]}

    def generate_onboarding_link(self, clientId):
        """https://docs.incode.com/docs/omni-api/api/onboarding#fetch-onboarding-url"""
        r = self.session.get(f"{self.base_url}/0/omni/onboarding-url?clientId={clientId}")
        response = r.json()
        return response
