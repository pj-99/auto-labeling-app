## CI/CD

## CD

Deploy services to GCP

- Backend app -> Cloud Run (Serverless)
    - `backend/app`
- Inference gateway -> Cloud Run (Serverless)
    - `models/gateway`
- Inference services -> Compute Engine (VM)
    - `models/sam` ... etc.

### Build Stage

Use GitHub actions to build new images when corresponding changes are made.


### Deploy stage

### Backend App and Inferences Gateway

Deploy the latest image to Cloud Run

### Inferences Services

Use Portainer on the VM to deploy the latest image.



--- 
