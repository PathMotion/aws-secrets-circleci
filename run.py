#!/usr/bin/env python3

import boto3
import json
import os
import argparse, sys

def main():
    if "KEY_ID" not in os.environ:
        raise ValueError('KEY_ID environment variable must be set for AWS Login')
    
    if "ACCESS_KEY" not in os.environ:
        raise ValueError('ACCESS_KEY environment variable must be set for AWS Login')

    aws_key_id = os.environ["KEY_ID"]
    aws_access_key = os.environ["ACCESS_KEY"]
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--secret', help = 'AWS Secret name', required = True)
    parser.add_argument('--region', help = 'AWS Region', required = True)
    parser.add_argument('--output', help = 'Output file where append the values', required = True)
    parser.add_argument('--debugcreds',
                            help = 'WARNING : Security risk. Should the AWS Credentials be displayed. You should revoke them soon after.',
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
    unseralizedSecret = json.loads(
        fetch_secret(secret_name, aws_region, aws_key_id, aws_access_key)
    )
    append_secrets_to_env_file(unseralizedSecret, output_file)
    print("Done.")

def append_secrets_to_env_file(secret, filepath):
    print("Appending secrets to file {}".format(filepath))

    if os.path.exists(filepath):
        writemode = 'a+'
    else:
        writemode = 'w+'
    
    file = open(filepath, writemode)
    for key,value in secret.items():
        print("\t exporting secret {}".format(key))
        escapedValue = value.translate(str.maketrans({
                                        "\"": "\\\"",
                                        "\n": ""
        }))
        file.write("export {}=\"{}\"\n".format(key,escapedValue))
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
    else:
        raise NotImplementedError("Binary secrets are not supported. Please set a Key Value secret.")

main()
