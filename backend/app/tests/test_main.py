import os
from uuid import UUID

import requests
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_image_upload_flow():
    # First get the signed URL
    signed_url_response = client.post(
        "/generate-signed-url", json={"content_type": "image/jpeg"}
    )
    assert signed_url_response.status_code == 200
    signed_url_data = signed_url_response.json()
    assert "filename" in signed_url_data
    assert "url" in signed_url_data

    # Prepare a test image
    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_image_path = os.path.join(current_dir, "test_image.jpg")

    # Create a small test image if it doesn't exist
    if not os.path.exists(test_image_path):
        with open(test_image_path, "wb") as f:
            f.write(b"fake image content")

    # Upload the image using the signed URL
    with open(test_image_path, "rb") as f:
        headers = {
            "Content-Type": "image/jpeg",
        }
        response = requests.put(
            signed_url_data["url"],
            data=open(test_image_path, "rb"),
            headers=headers,
        )

    assert response.status_code == 200

    # Clean up the test image
    os.remove(test_image_path)


def test_create_dataset():
    # GraphQL mutation for creating a dataset
    mutation = """
        mutation {
            createDataset(
                userId: "123e4567-e89b-12d3-a456-426614174000",
                name: "pytest"
            ) {
                id
                name
                createdBy
                createdAt
                updatedAt
            }
        }
    """

    # Execute the mutation
    response = client.post("/graphql", json={"query": mutation})

    # Check if the request was successful
    assert response.status_code == 200

    # Parse the response
    data = response.json()
    assert "errors" not in data, f"GraphQL errors: {data.get('errors')}"
    assert "data" in data
    assert "createDataset" in data["data"]

    # Verify the returned dataset
    dataset = data["data"]["createDataset"]
    assert dataset["name"] == "pytest"
    assert UUID(dataset["createdBy"]) == UUID("123e4567-e89b-12d3-a456-426614174000")
    assert "id" in dataset
    assert "createdAt" in dataset
    assert "updatedAt" in dataset

    return dataset["id"]


def test_insert_image_to_dataset():
    dataset_id = test_create_dataset()

    # GraphQL mutation for inserting an image to a dataset
    mutation = (
        r"""
        mutation {
            insertImageToDataset(
                userId: "123e4567-e89b-12d3-a456-426614174000",
                datasetId: "%s",
                imageUrl: "https://example.com/image.jpg",
                imageName: "test_image"
            ) { 
                id
                imageName
                imageUrl
                createdBy
                createdAt
                updatedAt
            }
        }
    """
        % dataset_id
    )

    # Execute the mutation
    response = client.post("/graphql", json={"query": mutation}).json()

    # Check if the request was successful
    assert "errors" not in response, f"GraphQL errors: {response.get('errors')}"
