import os
import boto3
from botocore.stub import Stubber
from src.fetch_exchange_rates import lambda_handler
from decimal import Decimal
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def test_lambda_handler():
    # Initialize DynamoDB client with a region and enable Stubber
    dynamodb = boto3.client('dynamodb', region_name=os.getenv('AWS_DEFAULT_REGION'))
    stubber = Stubber(dynamodb)

    # Simulate a successful `put_item` response
    stubber.add_response(
        'put_item',
        {},  # DynamoDB `put_item` doesn’t return data on success
        {
            'TableName': 'CurrencyExchangeRates',
            'Item': {
                'currency': {'S': 'USD'},
                'date': {'S': '2024-11-04'},
                'rate': {'N': Decimal('1.23')}
            }
        }
    )

    # Activate the stubber
    stubber.activate()

    # Run the lambda function with stubbed DynamoDB client
    with stubber:
        lambda_handler(None, None)

    # Verify no errors and deactivate stubber
    stubber.deactivate()
