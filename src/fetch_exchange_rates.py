import requests
import boto3
from datetime import datetime
import defusedxml.ElementTree

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('CurrencyExchangeRates')

def lambda_handler(event, context):
    # Fetch data from ECB
    response = requests.get('https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml')
    if response.status_code != 200:
        raise Exception("Failed to fetch data from ECB")

    data = parse_exchange_data(response.content)
    current_date = str(datetime.utcnow().date())

    # Store data in DynamoDB
    with table.batch_writer() as batch:
        for currency, rate in data.items():
            batch.put_item(
                Item={
                    'currency': currency,
                    'date': current_date,
                    'rate': float(rate)
                }
            )

def parse_exchange_data(xml_data):
    root = defusedxml.ElementTree.fromstring(xml_data)
    namespaces = {'ns': 'http://www.ecb.int/vocabulary/2002-08-01/eurofxref'}
    rates = {}
    
    for cube in root.findall(".//ns:Cube[@currency]", namespaces=namespaces):
        currency = cube.get('currency')
        rate = cube.get('rate')
        rates[currency] = rate

    return rates
