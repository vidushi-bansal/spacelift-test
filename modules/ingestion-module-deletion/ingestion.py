#!/usr/bin/env python3

import sys
import json
import boto3
from datetime import datetime

# Define required fields per resource type
REQUIRED_FIELDS = {
    "vpc": ["vpc_id", "region", "account_name", "created_by"],
    "subnet": ["subnet_id", "region", "account_name", "vpc_id", "created_by"],
    "instance": ["instance_id", "region", "vpc_id", "subnet_id", "security_groups", "created_by"]
}

# Define primary key field for each resource type
PRIMARY_KEYS = {
    "vpc": "vpc_id",
    "subnet": "subnet_id",
    "instance": "instance_id"
}

def parse_kv_args(kv_list):
    data = {}
    for arg in kv_list:
        if '=' in arg:
            key, value = arg.split("=", 1)
            val_lower = value.strip().lower()
            if val_lower == "true":
                data[key.strip()] = True
            elif val_lower == "false":
                data[key.strip()] = False
            else:
                data[key.strip()] = value.strip()
    return data

def ingest_to_dynamodb(host, resource_type, data):
    required = REQUIRED_FIELDS.get(resource_type)
    primary_key = PRIMARY_KEYS.get(resource_type)

    if not required or not primary_key:
        print(f"[!] Unknown or unsupported resource type: {resource_type}")
        sys.exit(1)

    # Check all required fields are present
    missing = [field for field in required if field not in data]
    if missing:
        print(f"[!] Missing required fields: {missing}")
        sys.exit(1)

    # Compose table name: <host>-<account_name>-<resource_type>
    table_name = f"{host}-{data['account_name']}-{resource_type}"

    # Prepare item
    item = {field: data[field] for field in required}
    item["timestamp"] = datetime.utcnow().isoformat() + "Z"
    item["Active"] = data.get("Active", True)

    # Store additional fields in raw_data
    excluded_keys = set(required) | {"Active"}
    raw_data = {k: v for k, v in data.items() if k not in excluded_keys}
    item["raw_data"] = json.dumps(raw_data)

    # DynamoDB upsert
    dynamodb = boto3.resource("dynamodb", region_name=data["region"])
    table = dynamodb.Table(table_name)

    # Perform upsert using put_item
    try:
        table.put_item(Item=item)
        print(f"[✓] {resource_type} data upserted into table '{table_name}' with {primary_key} = {data[primary_key]}")
    except Exception as e:
        print(f"[✗] Error while writing to DynamoDB: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python ingestion.py <host> <resource_type> key1=val1 key2=val2 ...")
        sys.exit(1)

    host = sys.argv[1]
    resource_type = sys.argv[2]
    kv_args = sys.argv[3:]
    data_map = parse_kv_args(kv_args)

    ingest_to_dynamodb(host, resource_type, data_map)
