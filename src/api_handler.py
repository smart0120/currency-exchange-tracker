import boto3
from boto3.dynamodb.conditions import Key
from decimal import Decimal
from datetime import datetime, timedelta, timezone

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('CurrencyExchangeRates')

def lambda_handler(event, context):
    current_date = str(datetime.now(timezone.utc).date())
    previous_date = str((datetime.now(timezone.utc) - timedelta(days=1)).date())

    current_rates = get_rates_by_date(current_date)
    previous_rates = get_rates_by_date(previous_date)

    result = calculate_changes(current_rates, previous_rates)

    return {
        'statusCode': 200,
        'body': result
    }

def get_rates_by_date(date):
    response = table.query(
        KeyConditionExpression=Key('date').eq(date)
    )
    return {item['currency']: item['rate'] for item in response.get('Items', [])}

def calculate_changes(current_rates, previous_rates):
    result = []
    for currency, current_rate in current_rates.items():
        previous_rate = previous_rates.get(currency)
        if previous_rate:
            change = ((Decimal(current_rate) - Decimal(previous_rate)) / Decimal(previous_rate)) * 100
            result.append({
                'currency': currency,
                'rate': str(current_rate),
                'change': str(round(change, 2))
            })
        else:
            result.append({
                'currency': currency,
                'rate': str(current_rate),
                'change': "N/A"
            })
    return result
