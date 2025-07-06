from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_label_crud():
    # Insert a label
    mutation = """
        mutation {
        upsertLabelDetections(
            datasetId:"123e4567-e89b-12d3-a456-426614174000", 
            imageId: "123e4567-e89b-12d3-a456-426614174000", 
            labelDetections : [      
            {
                classId: 0,
                xCenter: 0.10
                yCenter: 0.120
                width: 0.12345
                height: 0.4
            }])
        {
                ... on UpsertLabelDetectionSuccess {
                success
                labels {
                    imageId
                    id
                    createdAt
                    updatedAt
                    width
                    height
                }
            }
            ... on UpsertLabelError {
                message
            }
        }
    }
    """

    response = client.post("/graphql", json={"query": mutation}).json()

    assert "errors" not in response, f"GraphQL errors: {response.get('errors')}"
    assert "id" in response["data"]["upsertLabelDetections"]["labels"][0]

    # Update the label
    inserted_id = response["data"]["upsertLabelDetections"]["labels"][0]["id"]

    mutation = (
        r"""
        mutation {
        upsertLabelDetections(
            datasetId:"123e4567-e89b-12d3-a456-426614174000", 
            imageId: "123e4567-e89b-12d3-a456-426614174000", 
            labelDetections : [      
            {
                id: "%s",
                classId: 0,
                xCenter: 0.10
                yCenter: 0.120
                width: 0.12345
                height: 0.999
            }])
        {
                ... on UpsertLabelDetectionSuccess {
                success
                labels {
                    imageId
                    id
                    createdAt
                    updatedAt
                    width
                    height
                }
            }
            ... on UpsertLabelError {
                message
            }
        }
    }
    """
        % inserted_id
    )

    response = client.post("/graphql", json={"query": mutation}).json()

    # Check if the request was successful
    assert "errors" not in response, f"GraphQL errors: {response.get('errors')}"

    # Check if the label was updated
    assert response["data"]["upsertLabelDetections"]["labels"][0]["id"] == inserted_id
    assert response["data"]["upsertLabelDetections"]["labels"][0]["height"] == 0.999

    # Delete the label
    mutation = (
        r"""
        mutation {
            deleteLabelDetections(labelId: "%s") {
                ... on DeleteLabelSuccess {
                    success
                }
            }
        }
    """
        % inserted_id
    )
    response = client.post("/graphql", json={"query": mutation}).json()
    assert "errors" not in response, f"GraphQL errors: {response.get('errors')}"
    assert response["data"]["deleteLabelDetections"]["success"] == True
