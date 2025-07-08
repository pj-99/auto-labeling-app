# Auto labeling app




## Getting Started (Local Development)

> Running locally, with GCS resources on the cloud

**1. Set up environment variables**

```sh
cp backend/app/.env.example backend/app/dev.env
# And fill in the env vars
```

**2. Set up credentials**

- Place the GCP service account JSON at `backend/app/gcp_service_account.json`

**3. Start Docker containers for backends**
```sh
docker-compose up
```

**4. Start frontend**
```sh
cd frontend/app
npm i
npm run dev
```

