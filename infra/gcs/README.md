# GCS bucket setup


1. Serivce account setup
2. CORS setup

```sh
gcloud storage buckets update gs://${GCP_STORAGE_BUCKET} --cors-file=cors-config.json
```
cor-config.json:
```json
[
    {
        "origin": [
            "*"
        ],
        "method": [
            "GET",
            "PUT",
            "POST"
        ],
        "responseHeader": [
            "Content-Type"
        ],
        "maxAgeSeconds": 3600
    }
]
```