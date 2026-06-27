# Terraform — Data Mesh Self-Service

## Prerequisites

- Azure CLI (`az login`)
- Terraform >= 1.5

## Usage

```bash
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values
terraform init
terraform plan
terraform apply
```

## Resources

- Resource Group
- PostgreSQL Flexible Server (4 databases: sales, marketing, finance, datamesh)
- Container Instances (Governance API + Portal)
- Storage Account (Data Lake)
