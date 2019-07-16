import boto3
import json
import os

# 
def main():
    secret_name = os.environ["SECRET_NAME"]
    aws_region = os.environ["AWS_REGION"]
    unseralizedSecret = json.loads(fetch_secret(secret_name, aws_region))
    export_secret_to_env(unseralizedSecret)

def export_secret_to_env(secret):
    filepath = os.path.join(os.environ['CF_VOLUME_PATH'], "env_vars_to_export")
    f = open(filepath, "w+")
    for key,value in secret.items():
        print("Exporting {}".format(key))
        escapedValue = value.translate(str.maketrans({";":  r"\;",
                                          "=":  r"\="}))
        f.write("{}={}\n".format(key,value))
    f.close()

def fetch_secret(secret_name, region_name):
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    fetch_secret_value_response = client.fetch_secret_value(
        SecretId=secret_name
    )

    # Decrypts secret using the associated KMS CMK.
    # Depending on whether the secret is a string or binary, one of these fields will be populated.
    if 'SecretString' in fetch_secret_value_response:
        return fetch_secret_value_response['SecretString']
    else:
        raise NotImplementedError("Binary secrets are not supported. Please set a Key Value secret.")

main()
