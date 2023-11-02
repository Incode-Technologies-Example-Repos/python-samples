import base64
import json
import subprocess
import curlify
import requests
from PIL import Image
import pprint
from io import BytesIO

########################
# INCODE SESSION CLASS #
########################


class Session:

    def __init__(self, base_url, api_key, documents=None, flow_id=None, admin_credentials=None) -> None:
        self.base_url = base_url
        self.api_key = api_key
        self.flow_id = flow_id
        self.documents = documents
        self.interview_id = ""
        self.admin_credentials = admin_credentials
        self.s = requests.Session()
        self.s.stream = False
        self.s.headers.update({"x-api-key": self.api_key, "api-version": "1.0"})
        self.executive_token = None
        self.session_scores = None
        self.session_ocr_data = None
        self.api_call_dict = {}
        self.authentication_result = None
        self.fetched_interview_images = {}
        self.generate_curl_request = True
        self.flow_configuration = {}
        self.single_session_api_data = {}
        self.fetched_events = {}
        self.isConfigDefaultOnboardingFlow = None
        self.isSessionComplete = None


    @staticmethod
    def do_base64_encoded(path):
        """Helper function to encode images (input the image filepath) into base64 representations."""
        file = open(path, "rb")
        file_bytes = file.read()
        file.close()
        return base64.b64encode(file_bytes).decode("utf-8")


    @staticmethod
    def do_base64_decoded(base64String):
        """A convenience function to decode base64 image representations into viewable images using PIL"""
        return Image.open(BytesIO(base64.b64decode(base64String)))


    @staticmethod
    def bigCopy(stringData):
        """Helper function for copying really long strings in stored variables to the macOS clipboard. Great for copying base64 images."""
        return subprocess.run("pbcopy", universal_newlines=True, input=stringData)


    @staticmethod
    def loadJson(filepath):
        file = open(filepath)
        data = json.load(file)
        file.close()
        return data
    

    @staticmethod
    def writeJson(dictionary, outputFileName="sample.json"):
        # Serializing json
        json_object = json.dumps(dictionary)
        with open(outputFileName, "w") as outfile:
            outfile.write(json_object)


    @staticmethod
    def generateCurl(session):
        """A convenience function for auto-generating a curl request."""
        return curlify.to_curl(session.request)


    @staticmethod
    def prettyPrint(obj):
        """A convenience function for printing large JSON or Dictionary objects in a more readable format."""
        printer = pprint.PrettyPrinter(indent=4)
        printer.pprint(obj)


    def start(self):
        """https://docs.incode.com/docs/omni-api/api/onboarding#start-onboarding"""
        r = self.s.post(
            self.base_url + "omni/start",
            json={"countryCode": "ALL", "configurationId": self.flow_id},
        )
        resp = r.json()
        self.interview_id = resp["interviewId"]
        self.client_id = resp["clientId"]
        self.s.headers.update(
            {
                "x-api-key": self.api_key,
                "X-Incode-Hardware-Id": resp["token"],
                "api-version": "1.0",
                "Content-type": "application/json",
            }
        )
        self.api_call_dict["start"] = r.request
        return resp


    def upload_selfie(self):
        """https://docs.incode.com/docs/omni-api/api/onboarding#add-faceselfie-image"""
        data = Session.do_base64_encoded(self.documents["selfie"])
        r = self.s.post(
            self.base_url + "omni/add/face/third-party?imageType=selfie",
            json={"base64Image": data},
        )
        self.api_call_dict["upload_selfie"] = r.request
        return r.json()


    def process_approve(self):
        """https://docs.incode.com/docs/omni-api/api/onboarding#approve-customer"""
        r = self.s.post(
            f"{self.base_url}omni/process/approve?interviewId={self.interview_id}",
            json={},
        )
        self.api_call_dict["process_approve"] = r.request
        return r.json()


    def process_face(self):
        """https://docs.incode.com/docs/omni-api/api/onboarding#process-face"""
        r = self.s.post(
            self.base_url + "omni/process/face",
            json={},
        )
        self.api_call_dict["process_face"] = r.request
        return r.json()


    def upload_front_id(self, onlyFront=False):
        """https://docs.incode.com/docs/omni-api/api/onboarding#add-front-side-of-id"""
        data = Session.do_base64_encoded(self.documents["front_id"])
        r = self.s.post(
            f"{self.base_url}omni/add/front-id/v2?onlyFront={str(onlyFront).lower()}",
            json={"base64Image": data},
        )
        self.api_call_dict["upload_front_id"] = r.request
        return r.json()


    def upload_back_id(self):
        """https://docs.incode.com/docs/omni-api/api/onboarding#add-back-side-of-id"""
        data = Session.do_base64_encoded(self.documents["back_id"])
        r = self.s.post(
            self.base_url + "omni/add/back-id/v2",
            json={"base64Image": data}
        )
        self.api_call_dict["upload_back_id"] = r.request
        return r.json()


    def process_id(self):
        """https://docs.incode.com/docs/omni-api/api/onboarding#process-id"""
        r = self.s.post(
            self.base_url + "omni/process/id",
            json={},
        )
        self.api_call_dict["process_id"] = r.request
        return r.json()


    def fetchExecutiveToken(self):
        """https://docs.incode.com/docs/omni-api/api/conference#login-admin-token"""
        self.s.headers.update(
            {
                "x-api-key": self.api_key,
                "api-version": "1.0",
                "Content-type": "application/json",
            }
        )
        r = self.s.post(self.base_url + "executive/log-in", json=self.admin_credentials)
        response = r.json()
        self.api_call_dict["fetchExecutiveToken"] = r.request
        self.executive_token = response["token"]
        return response


    def get_scores(self, useExecutiveToken=True, manualInterviewId=None):
        """https://docs.incode.com/docs/omni-api/api/onboarding#fetch-scores"""
        if useExecutiveToken and manualInterviewId:
            self.interview_id = manualInterviewId
            self.s.headers.update({"X-Incode-Hardware-Id": self.executive_token})
        r = self.s.get(f"{self.base_url}omni/get/score/?id={self.interview_id}&verbose=true")
        response = r.json()
        self.session_scores = response
        self.api_call_dict["get_scores"] = r.request
        return response


    def get_ocr(self, useExecutiveToken=True, manualInterviewId=None):
        """https://docs.incode.com/docs/omni-api/api/onboarding#fetch-ocr-data"""
        if useExecutiveToken and manualInterviewId:
            self.interview_id = manualInterviewId
            self.s.headers.update({"X-Incode-Hardware-Id": self.executive_token})
        r = self.s.get(f"{self.base_url}omni/get/ocr-data?id={self.interview_id}")
        response = r.json()
        self.session_ocr_data = response
        self.api_call_dict["get_ocr"] = r.request
        return response


    def finish(self):
        """https://docs.incode.com/docs/omni-api/api/onboarding#mark-onboarding-complete"""
        r = self.s.get(self.base_url + "omni/finish-status")
        self.api_call_dict["finish"] = r.request


    def delete_session(self, useExecutiveToken=True, manualInterviewId=None):
        """https://docs.incode.com/docs/omni-api/api/onboarding#delete-single-onboarding-session"""
        if useExecutiveToken and manualInterviewId:
            self.interview_id = manualInterviewId
            self.s.headers.update({"X-Incode-Hardware-Id": self.executive_token})
        r = self.s.delete(f"{self.base_url}omni/interview?interviewId={self.interview_id}")
        response = r.json()
        self.api_call_dict["delete_session"] = r.request
        return response


    def generate_onboarding_link(self, clientId):
        """https://docs.incode.com/docs/omni-api/api/onboarding#fetch-onboarding-url"""
        r = self.s.get(f"{self.base_url}omni/onboarding-url?clientId={clientId}")
        response = r.json()
        self.api_call_dict["generate_onboarding_link"] = r.request
        return response


    def one_to_one_identifyV2(self, identifierType="uuid", identifier=None, generateCurlRequest=False):
        """https://docs.incode.com/docs/omni-api/api/login#face-authentication-11-v20"""
        data = Session.do_base64_encoded(self.documents["selfie"])
        r = self.s.post(
            f"{self.base_url}omni/1to1/identify/third-party",
            json={identifierType: identifier, "selfie": {"base64Image": data}},
        )
        self.authentication_result = r.json()
        if generateCurlRequest:
            print(Session.generateCurl(r))
        return self.authentication_result


    def get_images(self, imageTypesList=["selfie"], useExecutiveToken=False, manualInterviewId=None):
        """https://docs.incode.com/docs/omni-api/api/onboarding#fetch-images"""
        if useExecutiveToken and manualInterviewId:
            self.interview_id = manualInterviewId
            self.s.headers.update({"X-Incode-Hardware-Id": self.executive_token})
        r = self.s.post(
            f"{self.base_url}omni/get/images?id={self.interview_id}",
            json={"images": imageTypesList},
        )
        self.fetched_interview_images = r.json()
        self.api_call_dict["get_images"] = r.request
        return self.fetched_interview_images


    def get_custom_fields(self, useExecutiveToken=True, manualInterviewId=None):
        """https://docs.incode.com/docs/omni-api/api/onboarding#get-custom-fields"""
        if useExecutiveToken and manualInterviewId:
            self.interview_id = manualInterviewId
            self.s.headers.update({"X-Incode-Hardware-Id": self.executive_token})
        r = self.s.get(f"{self.base_url}omni/get/custom-fields?id={self.interview_id}")
        self.api_call_dict["get_custom_fields"] = r.request
        response = r.json()
        return response


    def get_user_consent(self, useExecutiveToken=True, manualInterviewId=None):
        if useExecutiveToken and manualInterviewId:
            self.interview_id = manualInterviewId
            self.s.headers.update({"X-Incode-Hardware-Id": self.executive_token})
        r = self.s.get(f"{self.base_url}omni/get/user-consent?id={self.interview_id}")
        self.api_call_dict["get_user_consent"] = r.request
        response = r.json()
        return response


    def get_phone_number(self, useExecutiveToken=True, manualInterviewId=None):
        if useExecutiveToken and manualInterviewId:
            self.interview_id = manualInterviewId
            self.s.headers.update({"X-Incode-Hardware-Id": self.executive_token})
        r = self.s.get(f"{self.base_url}omni/get/phone?id={self.interview_id}")
        self.api_call_dict["get_phone_number"] = r.request
        response = r.json()
        return response


    def get_email_address(self, useExecutiveToken=True, manualInterviewId=None):
        if useExecutiveToken and manualInterviewId:
            self.interview_id = manualInterviewId
            self.s.headers.update({"X-Incode-Hardware-Id": self.executive_token})
        r = self.s.get(f"{self.base_url}omni/get/email?id={self.interview_id}")
        self.api_call_dict["get_email_address"] = r.request
        response = r.json()
        return response


    def get_events(self, useExecutiveToken=True, manualInterviewId=None):
        """https://docs.incode.com/docs/omni-api/api/onboarding#fetch-events"""
        if useExecutiveToken and manualInterviewId:
            self.interview_id = manualInterviewId
            self.s.headers.update({"X-Incode-Hardware-Id": self.executive_token})
        r = self.s.get(f"{self.base_url}omni/get/events?id={self.interview_id}")
        response = r.json()
        self.fetched_events = response
        self.api_call_dict["get_events"] = r.request
        return response


    def get_flow_configuration(self, useExecutiveToken=True, manualFlowId=None):
        if useExecutiveToken and manualFlowId:
            self.flow_id = manualFlowId
            self.s.headers.update({"X-Incode-Hardware-Id": self.executive_token})
        r = self.s.get(f"{self.base_url}omni/flow/{self.flow_id}")
        response = r.json()
        self.api_call_dict["get_flow_configuration"] = r.request
        self.flow_configuration = response
        return response
