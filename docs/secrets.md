# Secrets to setup this APP

### `jwt-pubic-key`: use for decode clerk signed JWT

- 1. create and setup the signed key in clerk

- 2. create a secret in GCP
```sh
gcloud secrets create auto-labeling-jwt-public \
--replication-policy="automatic" \
--data-file="backend/app/jwt_public.pem"
```

- 3. set that secret to cloud run
```sh
gcloud run services update backend-app \
--set-secrets /secrets/clerk_jwt_public.pem=auto-labeling-jwt-public:latest
```

