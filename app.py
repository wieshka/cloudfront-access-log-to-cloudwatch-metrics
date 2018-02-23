# -*- coding: utf-8 -*-
import boto3
import csv
import gzip
import datetime 
import os

NAMESPACE = "CloudFront/Accesslogs"
CSV_FIELDS = (
    'date', # yyyy-mm-dd
    'time', # hh:mm:ss UTC
    'x-edge-location', # three-letter code and an arbitrarily assigned number, for example, DFW3. International Air Transport Association airport code
    'sc-bytes', # total number of bytes that CloudFront served
    'c-ip', # 192.0.2.183 or 2001:0db8:85a3:0000:0000:8a2e:0370:7334
    'cs-method', # Method DELETE, GET, HEAD, OPTIONS, PATCH, POST, or PUT.
    'cs(Host)', # The domain name of the CloudFront distribution, for example, d111111abcdef8.cloudfront.net.
    'cs-uri-stem', # The portion of the URI that identifies the path and object, for example, /images/daily-ad.jpg.
    'sc-status', # HTTP Status code: http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html
    'cs(Referer)', # The name of the domain that originated the request.
    'cs(User-Agent)', # The value of the User-Agent header in the request. 
    'cs-uri-query', # The query string portion of the URI, if any. (-)/hyphen for empty
    'cs(Cookie)', # The cookie header in the request, including name-value pairs and the associated attributes.
    'x-edge-result-type', # How CloudFront classifies the response after the last byte left the edge location. Hit / RefreshHit / Miss / LimitExceeded / CapacityExceeded / Error / Redirect
    'x-edge-request-id', # An encrypted string that uniquely identifies a request.    
    'x-host-header', # The value that the viewer included in the Host header for this request. This is the domain name in the request:
    'cs-protocol', # The protocol that the viewer specified in the request, either http or https.
    'cs-bytes', # The number of bytes of data that the viewer included in the request (client to server bytes), including headers.
    'time-taken', # The number of seconds from request received -> last byte served. 
    'x-forwarded-for', # X-Forwarded-For if used
    'ssl-protocol', # SSLv3 / TLSv1 / TLSv1.1 / TLSv1.2 & (-) for http
    'ssl-cipher', # SSL Cipher in use.
    'x-edge-response-result-type', # How CloudFront classified the response just before returning the response to the viewer. Hit / RefreshHit / Miss / LimitExceeded / CapacityExceeded / Error / Redirect
    'cs-protocol-version', # HTTP/0.9, HTTP/1.0, HTTP/1.1, and HTTP/2.0.
    'fle-status', # When field-level encryption is configured for a distribution, a code that indicates whether the request body was successfully processed.
    'fle-encrypted-fields'# The number of fields that CloudFront encrypted and forwarded to the origin. 
)


s3_client = boto3.client('s3')
cw_client = boto3.client('cloudwatch')
save_to = '/tmp/log.gz'


def fetch_file(file, bucket):
    s3_client.download_file(bucket, file, save_to)


def put_to_cloudwatch(metrics, namespace=NAMESPACE):
    response = cw_client.put_metric_data(
        Namespace=NAMESPACE,
        MetricData=metrics
    )


def line_to_metric(name, data, timestamp, ctype="Count"):
    metric = {
                'MetricName': name,
                'Timestamp': timestamp,
                'Value': float(data),
                'Unit': ctype,
                'StorageResolution': 60
            }
    return metric


def parse_log_file(logfile, bucket):
    fetch_file(logfile, bucket)
    metrics = []
    rn = 1
    with gzip.open(save_to, 'rt') as logdata:
        result = csv.DictReader(logdata, fieldnames=CSV_FIELDS, dialect="excel-tab")
        for row in result:
            if rn > 2:
                date = row.pop('date')
                row['timestamp'] = datetime.datetime.strptime(
                date + " " + row.pop('time'), '%Y-%m-%d %H:%M:%S').isoformat()
                if len(metrics) > 19:
                    put_to_cloudwatch(metrics)
                    metrics = []
                metrics.append(line_to_metric(row["x-edge-response-result-type"], 1, row['timestamp']))

            rn = rn + 1
    print("Access log {0} originating from {1} with {2} lines was parsed and pushed to CloudWatch".format(logfile, bucket, rn))


def lambda_handler(event, context):
    s3data = event["Records"][0]["s3"]
    key = s3data["object"]["key"]
    bucket = s3data["bucket"]["name"]
    result = parse_log_file(key, bucket)
    return "Done"