import calendar
import json

import boto3
from botocore.exceptions import ClientError


def lambda_handler(event, context):

    summary = {
        'BALANCE': 0.0,
        'MONTH_TXNS': {},
        'DEBIT_TXNS': 0,
        'DEBIT_AMOUNT': 0.0,
        'AVG_DEBIT_AMOUNT': 0.0,
        'CREDIT_TXNS': 0,
        'CREDIT_AMOUNT': 0.0,
        'AVG_CREDIT_AMOUNT': 0.0,
    }

    s3_client = boto3.client('s3')
    ddb_client = boto3.client('dynamodb')

    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    obj = s3_client.get_object(Bucket=bucket, Key=key)
    data = obj['Body'].read().decode('utf-8')

    records = data.split('\n')

    try:
        for record in records[1:]:
            id, txn_date, txn = tuple(record.split(','))
            ddb_writer(ddb_client, id, txn_date, txn)
            process_data(summary, id, txn_date, txn)

        summary['AVG_DEBIT_AMOUNT'] = summary['DEBIT_AMOUNT'] / \
            summary['DEBIT_TXNS']
        summary['AVG_CREDIT_AMOUNT'] = summary['CREDIT_AMOUNT'] / \
            summary['DEBIT_TXNS']

        send_email(summary)
    except Exception as e:
        print(e)


def ddb_writer(ddb_client, id, txn_date, txn):
    ddb_client.put_item(
        TableName='StoriRecords',
        Item={
            'Id': {'S': id},
            'Date': {'S': txn_date},
            'Txn': {'S': txn}
        }
    )


def process_data(summ_dict, id, txn_date, txn):
    month_number = int(txn_date.split('/')[0])
    month_name = calendar.month_name[month_number]

    if month_number not in summ_dict['MONTH_TXNS']:
        summ_dict['MONTH_TXNS'][month_number] = {
            'NAME': month_name,
            'TXNS': 0,
        }

    summ_dict['BALANCE'] += float(txn)
    summ_dict['MONTH_TXNS'][month_number]['TXNS'] += 1

    if '+' in txn:
        summ_dict['DEBIT_TXNS'] += 1
        summ_dict['DEBIT_AMOUNT'] += float(txn)

    if '-' in txn:
        summ_dict['CREDIT_TXNS'] += 1
        summ_dict['CREDIT_AMOUNT'] += float(txn)


def send_email(summ_dict):
    SENDER = "apema2079@gmail.com"
    RECIPIENT = "apema2079@gmail.com"
    AWS_REGION = "us-east-1"
    SUBJECT = "Stori data process summary"
    CHARSET = "UTF-8"

    body_text = ""
    body_html = "<html><head></head><body>"

    body_text += f"Total balance id {summ_dict['BALANCE']}\n"
    body_html += f"<h1>Total balance is {summ_dict['BALANCE']}</h1><br><br><ul>"

    sorted_month_txns = dict(sorted(summ_dict['MONTH_TXNS'].items()))
    for month_details in sorted_month_txns.values():
        body_text += f"Number of transaction in {month_details['NAME']}: {month_details['TXNS']}\n"
        body_html += f"<li>Number of transaction in {month_details['NAME']}: {month_details['TXNS']}</li>"

    body_html += "</ul><br><br>"

    body_text += f"Average debit amount: {summ_dict['AVG_DEBIT_AMOUNT']}\n"
    body_text += f"Average credit amount: {summ_dict['AVG_CREDIT_AMOUNT']}\n"

    body_html += f"<h3>Average debit amount: {summ_dict['AVG_DEBIT_AMOUNT']}</h3>"
    body_html += f"<h3>Average credit amount: {summ_dict['AVG_CREDIT_AMOUNT']}</h3><br>"

    client_ses = boto3.client('ses', region_name=AWS_REGION)

    try:
        response = client_ses.send_email(
            Destination={
                'ToAddresses': [
                    RECIPIENT
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': body_html,
                    },
                    'Text': {
                        'Charset': CHARSET,
                        'Data': body_text,
                    },
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': SUBJECT
                },
            },
            Source=SENDER,
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print(f"Email sent! Message ID: {response['MessageId']}"),
