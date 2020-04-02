#!/usr/bin/env python3

import json
import os
import argparse
import boto3

def main():
    if "KEY_ID" not in os.environ:
        raise ValueError('KEY_ID environment variable must be set for AWS Login')

    if "ACCESS_KEY" not in os.environ:
        raise ValueError('ACCESS_KEY environment variable must be set for AWS Login')

    aws_key_id = os.environ["KEY_ID"]
    aws_access_key = os.environ["ACCESS_KEY"]

    parser = argparse.ArgumentParser()
    parser.add_argument('--secret', help='AWS Secret name', required=True)
    parser.add_argument('--region', help='AWS Region', required=True)
    parser.add_argument('--output', help='Output file where append the values', required=True)
    parser.add_argument('--no-prepend-export',
                        help='Do not prepend the values with export',
                        action='store_true')
    parser.add_argument('--debugcreds',
                        help='''WARNING : Security risk.
                                Should the AWS Credentials be displayed.
                                You should revoke them soon after.''',
                        action='store_true')
    args = parser.parse_args()

    if args.debugcreds:
        print("Creds debugging:")
        print("KEY ID is {}".format(aws_key_id))
        print("ACCESS KEY is {}".format(aws_access_key))
        print("☣️Please revoke those credentials asap ☣️")

    secret_name = args.secret
    aws_region = args.region
    output_file = args.output
    unseralized_secret = json.loads(
        fetch_secret(secret_name, aws_region, aws_key_id, aws_access_key)
    )
    append_secrets_to_env_file(unseralized_secret, output_file, not args.no_prepend_export)
    print("Done.")

def append_secrets_to_env_file(secret, filepath, prepend_with_export=True):
    print("Appending secrets to file {}".format(filepath))

    export_keyword = "export "
    if not prepend_with_export:
        export_keyword = ""
        print("Export will not be prepended")

    if os.path.exists(filepath):
        writemode = 'a+'
    else:
        writemode = 'w+'

    file = open(filepath, writemode)
    for key, value in secret.items():
        print("\t exporting secret {}".format(key))
        escaped_value = value.translate(str.maketrans({
            "\"": "\\\"",
            "\n": ""
        }))
        file.write("{}{}=\"{}\"\n".format(export_keyword, key, escaped_value))
    file.close()

def fetch_secret(secret_name, region_name, aws_key_id, aws_access_key):
    print("Fetching from AWS Secrets Manager")
    print("\tsecret: {} ".format(secret_name))
    print("\tregion: {}".format(region_name))

    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name,
        aws_access_key_id=aws_key_id,
        aws_secret_access_key=aws_access_key
    )

    get_secret_value_response = client.get_secret_value(
        SecretId=secret_name
    )

    # Decrypts secret using the associated KMS CMK.
    # Depending on whether the secret is a string or binary, one of these fields will be populated.
    if 'SecretString' in get_secret_value_response:
        return get_secret_value_response['SecretString']
    raise NotImplementedError('''Binary secrets are not supported.
        Please set a Key Value secret.''')

main()
