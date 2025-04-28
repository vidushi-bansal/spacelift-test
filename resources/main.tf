module "ingest_vpc" {
  source        = "../../modules/ingestion-module-deletion"
  host          = "aws"
  resource_type = "vpc"
  revision = true
  data_map = {
    vpc_id       = aws_vpc.dev.id
    region       = "us-east-1"
    account_name = "dev"
    created_by   = "dev-team"
    cidr_block   = aws_vpc.dev.cidr_block
    name         = aws_vpc.dev.tags["Name"]
  }
}

resource "aws_vpc" "dev" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  tags = {
    Name        = "dev-vpc"
    Environment = "dev"
  }
}
