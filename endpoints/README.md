# Ometry Atlas API Endpoints for App Engine Standard

### Summary
- Endpoints uses the [Extensible Service Proxy\(ESP\)](https://cloud.google.com/endpoints/docs/openapi/glossary#extensible_service_proxy) as an API gateway. We have the prebuilt ESP container deployed to Cloud Run and we have secured our Ometry Atlas app(backend) secured by [Identity Aware Proxy\(IAP\)](https://cloud.google.com/iap), so that only ESP can envoke it. 
- Although Endpoints proxys requests to GAE, it is independent of GAE, which means when a new route or changes of parameters to the existing routes are added to the backend application, Endpoints must also be updated accordingly to proxy the requests to the backend application by updating the OpenAPI configurations. Only then, will Endpoints serve the requests properly and Developer Portal will also reflect the updates

### Deployment
- We must have an OpenAPI document based on [Open API Speicification v2.0](https://github.com/OAI/OpenAPI-Specification/blob/master/versions/2.0.md#specification) that describes the surface of our app and any authentication requirements.
- The specifications on the document will reflect Developer Portal
- Command to deploy
  - ```gcloud endpoints services deploy openapi-appengine.yaml --project ESP_PROJECT_ID```
  - The command above assumes 'openapi-appengine.yaml' in the current directory
  
### Sample Code
```
swagger: '2.0'
info:
  title: Cloud Endpoints + App Engine
  description: Sample API on Cloud Endpoints with an App Engine backend
  version: 1.0.0
host: HOST
schemes:
  - https
produces:
  - application/json
x-google-backend:
  address: https://APP_PROJECT_ID.REGION.r.appspot.com
  jwt_audience: IAP_CLIENT_ID
  protocol: h2
paths:
  /:
    get:
      summary: Greet a user
      operationId: hello
      responses:
        '200':
          description: A successful response
          schema:
            type: string
```

### Quota
- Currently we have a quota of 5,000 per min. So, Endpoints will not allow more than 5,000 requests per minute.
- [To configuring quotas](https://cloud.google.com/endpoints/docs/openapi/quotas-configure)



