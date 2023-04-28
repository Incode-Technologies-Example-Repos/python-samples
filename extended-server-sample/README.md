# Example Token Server Using Python

## Endpoints

- `/start`: Call Incode's `omni/start` API to create an Incode session which will include a token in the JSON response.  This token can be shared with Incode SDK client apps to do token based initialization.

- `/onboarding-url`: For the vanilla implementation this is called subsequent to starting the session with the `/start` endpoint and calls incodes `/omni/onboarding-url` endpoint. For the security optimized implementation, `/onboarding-url-without-api-key` will call `0/omni/onboarding-url` to retrieve the unique onboarding-url without the API key in the header. If you plan to include the API key and the token in the header, you will use `/omni/onboarding-url` as the route (i.e. without the `0/`).

- `/executive-token`: This endpoint will generate an executive token that can be used to access Incode API endpoints, independent of starting a new session and using the token returned by the `/start` endpoint. For example, if you want to send the onboarding URL to a customer via our SMS API endpoint, you will use the executive token for the `X-Incode-Hardware-Id` header instead of the token returned by the `/start` endpoint. You can also use this token for other tasks such as, fetching scores or OCR data for a particular session at a later point in time. 

## Prerequisites

Run: `pip install -r requirements.txt`

## Local Development

### Environment

Rename `sample.env` file to `.env` and add your client details:

```env
API_URL = https://demo-api.incodesmile.com
API_KEY = API Key from your delivery document
API_VERSION = 1.0 
CLIENT_ID = your-client-id
FLOW_ID = Flow Id from your Incode dashboard.
HTTP_PORT = The port you want your localhost to connect to.
ADMIN_EMAIL = Username/email from your delivery doc (optional). Only necessary if you're using the `/executive/log-in` endpoint.
ADMIN_PASSWORD = Password from your delivery doc (optional). Only necessary if you're using the `/executive/log-in` endpoint.
SELFIE_PATH = Optional. Necessary if you're using the `/omni/add/face/third-party` endpoint.
FRONT_ID_PATH = Optional. Necessary if you're using the `/omni/add/front-id/v2` endpoint.
BACK_ID_PATH = Optional. Necessary if you're using the `/omni/add/back-id/v2` endpoint.
```

### Expose the server to the internet for frontend testing with ngrok

The server will accept petitions on `http://localhost:8080/`.
First you need an ngrok account properly configured on your computer. You can visit `https://ngrok.com` to make a free account and do a quick setup. Then, to expose the server to the internet through your ngrok account, run the following:

```bash
ngrok http 8080
```

Open the `Forwarding` adress in a web browser. The URL should look similar to this: `https://466c-47-152-68-211.ngrok-free.app`.
In a separate terminal, run the server.py script with the command below:

```bash
python3 server.py
```

Now you should be able to visit the following routes to receive the associated payloads:
1. `https://yourforwardingurl.app/start`
2. `https://yourforwardingurl.app/onboarding-url`
3. `https://yourforwardingurl.app/onboarding-url-without-api-key`
4. `https://yourforwardingurl.app/executive-token`

For your convenience, the `/start` API call was included in each of the onboarding URL generation endpoints, so you do not need to call the `/start` endpoint individually in order to generate the onboarding URL.

If you want to test generating the onboarding URL without including the API key in the header, use the `/onboarding-url-without-api-key` route like this:
`https://yourforwardingurl.app/onboarding-url-without-api-key`


## Dependencies
* **python3**: Programming language for this demo.
* **ngrok**: Unified ingress platform used to expose your local server to the internet.
* **dotenv**: Used to access environment variables.
