# -*- coding: utf-8 -*-
import boto3
import csv
import gzip
import datetime 
import os
import logging

NAMESPACE = "CloudFront/Accesslogs"
# CSV_FIELDS = [
#     'date', #0 yyyy-mm-dd
#     'time', #1 hh:mm:ss UTC
#     'x-edge-location', #2 three-letter code and an arbitrarily assigned number, for example, DFW3. International Air Transport Association airport code
#     'sc-bytes', #3 total number of bytes that CloudFront served
#     'c-ip', #4 192.0.2.183 or 2001:0db8:85a3:0000:0000:8a2e:0370:7334
#     'cs-method', #5 Method DELETE, GET, HEAD, OPTIONS, PATCH, POST, or PUT.
#     'cs(Host)', #6 The domain name of the CloudFront distribution, for example, d111111abcdef8.cloudfront.net.
#     'cs-uri-stem', #7 The portion of the URI that identifies the path and object, for example, /images/daily-ad.jpg.
#     'sc-status', #8 HTTP Status code: http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html
#     'cs(Referer)', #9 The name of the domain that originated the request.
#     'cs(User-Agent)', #10 The value of the User-Agent header in the request. 
#     'cs-uri-query', #11 The query string portion of the URI, if any. (-)/hyphen for empty
#     'cs(Cookie)', #12 The cookie header in the request, including name-value pairs and the associated attributes.
#     'x-edge-result-type', #13 How CloudFront classifies the response after the last byte left the edge location. Hit / RefreshHit / Miss / LimitExceeded / CapacityExceeded / Error / Redirect
#     'x-edge-request-id', #14 An encrypted string that uniquely identifies a request.    
#     'x-host-header', #15 The value that the viewer included in the Host header for this request. This is the domain name in the request:
#     'cs-protocol', #16 The protocol that the viewer specified in the request, either http or https.
#     'cs-bytes', #17 The number of bytes of data that the viewer included in the request (client to server bytes), including headers.
#     'time-taken', #18 The number of seconds from request received -> last byte served. 
#     'x-forwarded-for', #19 X-Forwarded-For if used
#     'ssl-protocol', #20 SSLv3 / TLSv1 / TLSv1.1 / TLSv1.2 & (-) for http
#     'ssl-cipher', #21 SSL Cipher in use.
#     'x-edge-response-result-type', #22 How CloudFront classified the response just before returning the response to the viewer. Hit / RefreshHit / Miss / LimitExceeded / CapacityExceeded / Error / Redirect
#     'cs-protocol-version', #23 HTTP/0.9, HTTP/1.0, HTTP/1.1, and HTTP/2.0.
#     'fle-status', #24 When field-level encryption is configured for a distribution, a code that indicates whether the request body was successfully processed.
#     'fle-encrypted-fields' #25 The number of fields that CloudFront encrypted and forwarded to the origin. 
# ]


s3c = boto3.client('s3')
cwc = boto3.client('cloudwatch')
logging.basicConfig(level=logging.INFO)
save_to = '/tmp/log.gz'


def fetch_file(file, bucket):
    s3c.download_file(bucket, file, save_to)


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

    with gzip.open(save_to, 'rt') as logdata:
        result = csv.DictReader(logdata)
            for row in in results:
                if len(metrics) == 20:
                    put_to_cloudwatch(metrics)
                    del metrics[:]
                timestamp = datetime.datetime.strptime("{date} {time}".format(**row), "%Y-%m-%d %H:%M:%S").isoformat()
                metrics.append(line_to_metric(row["x-edge-response-result-type"], 1, timestamp))

    logging.info("Access log {0} originating from {1} with {2} lines was parsed and pushed to CloudWatch".format(logfile, bucket, rn))


def lambda_handler(event, context):
    s3data = event["Records"][0]["s3"]
    key = s3data["object"]["key"]
    bucket = s3data["bucket"]["name"]
    result = parse_log_file(key, bucket)
    return "Done"