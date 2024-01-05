# Example Token Server Using Python

## Endpoints

- GET `/start`: Call Incode's `/omni/start` API to create an Incode session which will include a token in the JSON response.  This token can be shared with Incode SDK client apps to do token based initialization, which is a best practice.

- GET `/onboarding-url`: Calls incodes `/omni/start` and then with the token calls `/0/omni/onboarding-url` to retrieve the unique onboarding-url for the newly created session.

It can receive the optional query parameter `redirectUrl` to set where to redirect the user at the end of the flow.

- POST `/webhook`: Example webhook that reads the json data and return it back a response, from here you could fetch scores or OCR data when the status is ONBOARDING_FINISHED

- POST `/approve`: Example webhook that reads the json data and if the status is ONBOARDING_FINISHED goes ahead and creates the identity using the `/omni/process/approve` endpoint.

## Secure Credential Handling
We highly recommend to follow the 0 rule for your implementations, where all sensitive calls to incode's endpoints are done in the backend, keeping your apikey protected and just returning a `token` with the user session to the frontend.

Within this sample you will find the only call to a `/omni/` endpoint we recommend for you to have, it requires the usage of the `apikey`, all further calls must be done using only the generated `token` and be addresed to the `/0/omni` endpoints. 

## Prerequisites
This sample requires [Python 3](https://www.python.org/downloads/) or superior with pip installed

## Local Development

### Environment
Rename `sample.env` file to `.env` and add your client details:

```env
API_URL=https://demo-api.incodesmile.com
API_KEY=you-api-key
CLIENT_ID=your-client-id
FLOW_ID=Flow Id from your Incode dashboard.
ADMIN_TOKEN=Needed for the webhooks to be able to fetch Scores and auto-approve
```

### Run Localy
Using pip install all the dependencies
```bash
pip install -r requirements.txt
```

Then start the local server with
```bash
python3 server.py
```

The server will accept petitions on `http://localhost:3000/`

### Expose the server to the internet for frontend testing with ngrok
For your frontend to properly work in tandem with this server on your mobile phone for testing, you will need a public url with proper SSL configured, by far the easiest way to acchieve this with an ngrok account properly configured on your computer. You can visit `https://ngrok.com` to make a free account and do a quick setup.

In another shell expose the server to internet through your computer ngrok account:

```bash
ngrok http 3000
```

Open the `Forwarding` adress in a web browser. The URL should look similar to this: `https://466c-47-152-68-211.ngrok-free.app`.

Now you should be able to visit the following routes to receive the associated payloads:
1. `https://yourforwardingurl.app/start`
2. `https://yourforwardingurl.app/onboarding-url`
3. `https://yourforwardingurl.app/onboarding-url?redirectionUrl=https%3A%2F%2Fexample.com%2F`

## Webhooks

### Simplified Webhook
`https://yourforwardingurl.app/webhook`
We provide an example on how to read the data we send in the webhook calls, from here you could
fetch scores and OCR data, what you do with that is up to you.

### Auto approve on OK
`https://yourforwardingurl.app/approve`
We provide a more complex example where we fetch the scores and if the status is `OK` we then
approve the user to create his identity for face-login

### Admin Token
For the approval and fetching of scores to work you will need an Admin Token, Admin tokens
require an executive user-password and have a 24 hour expiration, thus need a
more involved strategy to be generated, renewed, securely saved and shared to the app.

For this simple test just use the following cURl, and add the generated token to the `.env` file,
you will need to refresh it after 24 hours.

```bash
curl --location 'https://demo-api.incodesmile.com/executive/log-in' \
--header 'Content-Type: application/json' \
--header 'api-version: 1.0' \
--header 'x-api-key: <your-apikey>' \
--data '{
    "email": "••••••",
    "password": "••••••"
}'
```

### How to test your code
To recreate the call and the format of the data sent by Incode you can use the following script:

```bash
curl --location 'https://yourforwardingurl.app/webhook' \
--header 'Content-Type: application/json' \
--data '{
    "interviewId": "<interviewId>",
    "onboardingStatus": "ONBOARDING_FINISHED",
    "clientId": "<clientId>",
    "flowId": "<flowId>"
}'
```

## Dependencies

* **python3**: Python is a high-level, general-purpose programming language.
* **ngrok**: Unified ingress platform used to expose your local server to the internet.
* **dotenv**: Used to access environment variables.