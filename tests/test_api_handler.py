import os
from unittest.mock import patch
from src.api_handler import lambda_handler
from decimal import Decimal
from moto import mock_aws
import boto3

# Set dummy AWS credentials as environment variables
os.environ["AWS_ACCESS_KEY_ID"] = "test_access_key"
os.environ["AWS_SECRET_ACCESS_KEY"] = "test_secret_key"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

@mock_aws(config={
    "batch": {"use_docker": True},
    "lambda": {"use_docker": True},
    "core": {
        "mock_credentials": True,
        "passthrough": {
            "urls": ["s3.amazonaws.com/bucket*"],
            "services": ["dynamodb"]
        },
        "reset_boto3_session": True,
        "service_whitelist": None,
    },
    "iam": {"load_aws_managed_policies": False},
    "stepfunctions": {"execute_state_machine": True},
    "iot": {"use_valid_cert": False},
})
def test_api_handler():
    # Initialize the mocked DynamoDB resource
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    
    # Create the table structure as expected by the application
    table = dynamodb.create_table(
        TableName="CurrencyExchangeRates",
        KeySchema=[
            {"AttributeName": "date", "KeyType": "HASH"},
            {"AttributeName": "currency", "KeyType": "RANGE"}
        ],
        AttributeDefinitions=[
            {"AttributeName": "date", "AttributeType": "S"},
            {"AttributeName": "currency", "AttributeType": "S"}
        ],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5}
    )

    # Insert mock data for today's and yesterday's rates
    table.put_item(Item={"currency": "USD", "date": "2024-11-04", "rate": Decimal("1.23")})
    table.put_item(Item={"currency": "EUR", "date": "2024-11-04", "rate": Decimal("0.85")})
    table.put_item(Item={"currency": "USD", "date": "2024-11-03", "rate": Decimal("1.22")})
    table.put_item(Item={"currency": "EUR", "date": "2024-11-03", "rate": Decimal("0.84")})

    # Call the Lambda handler
    response = lambda_handler({}, None)

    # Verify response format and content
    assert response["statusCode"] == 200
    assert isinstance(response["body"], list)
    assert response["body"][0]["currency"] == "USD"
    assert "rate" in response["body"][0]
    assert "change" in response["body"][0]
