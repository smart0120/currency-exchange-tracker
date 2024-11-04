# Currency Exchange Tracker

This application is a currency exchange rate tracker that fetches exchange rates daily from the European Central Bank, stores them in a DynamoDB table, and exposes an API for current exchange rate data and daily rate changes.

## Setup

1. Clone this repository.
2. Ensure you have an AWS account and the AWS CLI configured.
3. Deploy the CloudFormation stack:
    ```bash
    aws cloudformation deploy --template-file infra/template.yaml --stack-name CurrencyExchangeTrackerStack --capabilities CAPABILITY_NAMED_IAM
    ```

## API Usage

Once deployed, access the API at the endpoint provided by the API Gateway. The /rates endpoint provides:

- Current exchange rates
- Daily change in rates

Example response:
    ```
    [
    {
        "currency": "USD",
        "rate": "1.1234",
        "change": "0.5"
    },
    ...
    ]
    ```

## Testing

Unit tests for the application are in the `tests/` folder. You can run them using `pytest`:
```
pytest tests/
```