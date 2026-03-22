"""
Hardcoded fallback pricing data for all providers.
Used when live API calls fail or credentials are not available.
"""


def get_aws_compute_data():
    """AWS compute pricing fallback (us-east-1, Linux)"""
    return [
        # US East (N. Virginia)
        {"region": "us-east-1", "instance_type": "t3.micro", "os": "Linux", "hourly": 0.0104, "vcpu": 2, "mem": 1.0},
        {"region": "us-east-1", "instance_type": "t3.small", "os": "Linux", "hourly": 0.0208, "vcpu": 2, "mem": 2.0},
        {"region": "us-east-1", "instance_type": "t3.medium", "os": "Linux", "hourly": 0.0416, "vcpu": 2, "mem": 4.0},
        {"region": "us-east-1", "instance_type": "t3.large", "os": "Linux", "hourly": 0.0832, "vcpu": 2, "mem": 8.0},
        {"region": "us-east-1", "instance_type": "m5.large", "os": "Linux", "hourly": 0.096, "vcpu": 2, "mem": 8.0},
        {"region": "us-east-1", "instance_type": "m5.xlarge", "os": "Linux", "hourly": 0.192, "vcpu": 4, "mem": 16.0},
        {"region": "us-east-1", "instance_type": "m5.2xlarge", "os": "Linux", "hourly": 0.384, "vcpu": 8, "mem": 32.0},
        {"region": "us-east-1", "instance_type": "c5.large", "os": "Linux", "hourly": 0.085, "vcpu": 2, "mem": 4.0},
        {"region": "us-east-1", "instance_type": "c5.xlarge", "os": "Linux", "hourly": 0.170, "vcpu": 4, "mem": 8.0},
        {"region": "us-east-1", "instance_type": "r5.large", "os": "Linux", "hourly": 0.126, "vcpu": 2, "mem": 16.0},
        # Windows variants (2x Linux price)
        {"region": "us-east-1", "instance_type": "t3.micro", "os": "Windows", "hourly": 0.0208, "vcpu": 2, "mem": 1.0},
        {"region": "us-east-1", "instance_type": "t3.small", "os": "Windows", "hourly": 0.0416, "vcpu": 2, "mem": 2.0},
        {"region": "us-east-1", "instance_type": "t3.medium", "os": "Windows", "hourly": 0.0832, "vcpu": 2, "mem": 4.0},
        {"region": "us-east-1", "instance_type": "m5.large", "os": "Windows", "hourly": 0.192, "vcpu": 2, "mem": 8.0},
        {"region": "us-east-1", "instance_type": "m5.xlarge", "os": "Windows", "hourly": 0.384, "vcpu": 4, "mem": 16.0},
        # US West (Oregon)
        {"region": "us-west-2", "instance_type": "t3.micro", "os": "Linux", "hourly": 0.0104, "vcpu": 2, "mem": 1.0},
        {"region": "us-west-2", "instance_type": "t3.medium", "os": "Linux", "hourly": 0.0416, "vcpu": 2, "mem": 4.0},
        {"region": "us-west-2", "instance_type": "m5.large", "os": "Linux", "hourly": 0.096, "vcpu": 2, "mem": 8.0},
        {"region": "us-west-2", "instance_type": "m5.xlarge", "os": "Linux", "hourly": 0.192, "vcpu": 4, "mem": 16.0},
        # Europe (Ireland)
        {"region": "eu-west-1", "instance_type": "t3.micro", "os": "Linux", "hourly": 0.0114, "vcpu": 2, "mem": 1.0},
        {"region": "eu-west-1", "instance_type": "t3.medium", "os": "Linux", "hourly": 0.0456, "vcpu": 2, "mem": 4.0},
        {"region": "eu-west-1", "instance_type": "m5.large", "os": "Linux", "hourly": 0.107, "vcpu": 2, "mem": 8.0},
        # Asia Pacific (Mumbai)
        {"region": "ap-south-1", "instance_type": "t3.micro", "os": "Linux", "hourly": 0.0104, "vcpu": 2, "mem": 1.0},
        {"region": "ap-south-1", "instance_type": "m5.large", "os": "Linux", "hourly": 0.096, "vcpu": 2, "mem": 8.0},
        # Asia Pacific (Singapore)
        {"region": "ap-southeast-1", "instance_type": "t3.micro", "os": "Linux", "hourly": 0.0116, "vcpu": 2, "mem": 1.0},
        {"region": "ap-southeast-1", "instance_type": "m5.large", "os": "Linux", "hourly": 0.107, "vcpu": 2, "mem": 8.0},
    ]


def get_aws_storage_data():
    """AWS storage pricing fallback"""
    return [
        # S3 (object storage) - same price across regions
        {"region": "us-east-1", "type": "object", "name": "S3 Standard", "price_gb_month": 0.023},
        {"region": "us-west-2", "type": "object", "name": "S3 Standard", "price_gb_month": 0.023},
        {"region": "eu-west-1", "type": "object", "name": "S3 Standard", "price_gb_month": 0.024},
        {"region": "ap-south-1", "type": "object", "name": "S3 Standard", "price_gb_month": 0.025},
        {"region": "ap-southeast-1", "type": "object", "name": "S3 Standard", "price_gb_month": 0.025},
        # EBS gp3 (block storage)
        {"region": "us-east-1", "type": "block", "name": "EBS gp3", "price_gb_month": 0.080},
        {"region": "us-west-2", "type": "block", "name": "EBS gp3", "price_gb_month": 0.080},
        {"region": "eu-west-1", "type": "block", "name": "EBS gp3", "price_gb_month": 0.089},
        {"region": "ap-south-1", "type": "block", "name": "EBS gp3", "price_gb_month": 0.095},
        {"region": "ap-southeast-1", "type": "block", "name": "EBS gp3", "price_gb_month": 0.088},
    ]


def get_aws_reserved_data():
    """AWS reserved instance pricing fallback (us-east-1, t3.medium Linux example)"""
    return [
        {"region": "us-east-1", "instance": "t3.medium", "os": "Linux", "term": "one_yr", "payment": "no_upfront", "upfront": 0, "monthly": 14.60, "eff_hourly": 0.020, "savings": 51.0},
        {"region": "us-east-1", "instance": "t3.medium", "os": "Linux", "term": "one_yr", "payment": "partial_upfront", "upfront": 88, "monthly": 7.30, "eff_hourly": 0.017, "savings": 59.0},
        {"region": "us-east-1", "instance": "t3.medium", "os": "Linux", "term": "one_yr", "payment": "all_upfront", "upfront": 175, "monthly": 0, "eff_hourly": 0.020, "savings": 52.0},
        {"region": "us-east-1", "instance": "t3.medium", "os": "Linux", "term": "three_yr", "payment": "all_upfront", "upfront": 290, "monthly": 0, "eff_hourly": 0.011, "savings": 74.0},
        {"region": "us-east-1", "instance": "m5.large", "os": "Linux", "term": "one_yr", "payment": "no_upfront", "upfront": 0, "monthly": 42.00, "eff_hourly": 0.058, "savings": 40.0},
        {"region": "us-east-1", "instance": "m5.large", "os": "Linux", "term": "one_yr", "payment": "all_upfront", "upfront": 504, "monthly": 0, "eff_hourly": 0.057, "savings": 41.0},
        {"region": "us-east-1", "instance": "m5.large", "os": "Linux", "term": "three_yr", "payment": "all_upfront", "upfront": 840, "monthly": 0, "eff_hourly": 0.032, "savings": 67.0},
    ]


def get_azure_compute_data():
    """Azure compute pricing fallback (eastus, Linux)"""
    return [
        {"region": "eastus", "instance_type": "Standard_B1s", "os": "Linux", "hourly": 0.0104, "vcpu": 1, "mem": 1.0},
        {"region": "eastus", "instance_type": "Standard_B2s", "os": "Linux", "hourly": 0.0416, "vcpu": 2, "mem": 4.0},
        {"region": "eastus", "instance_type": "Standard_B4ms", "os": "Linux", "hourly": 0.166, "vcpu": 4, "mem": 16.0},
        {"region": "eastus", "instance_type": "Standard_D2s_v3", "os": "Linux", "hourly": 0.096, "vcpu": 2, "mem": 8.0},
        {"region": "eastus", "instance_type": "Standard_D4s_v3", "os": "Linux", "hourly": 0.192, "vcpu": 4, "mem": 16.0},
        {"region": "eastus", "instance_type": "Standard_D8s_v3", "os": "Linux", "hourly": 0.384, "vcpu": 8, "mem": 32.0},
        {"region": "eastus", "instance_type": "Standard_F2s_v2", "os": "Linux", "hourly": 0.085, "vcpu": 2, "mem": 4.0},
        {"region": "eastus", "instance_type": "Standard_F4s_v2", "os": "Linux", "hourly": 0.170, "vcpu": 4, "mem": 8.0},
        {"region": "eastus", "instance_type": "Standard_E2s_v3", "os": "Linux", "hourly": 0.126, "vcpu": 2, "mem": 16.0},
        # Windows
        {"region": "eastus", "instance_type": "Standard_B2s", "os": "Windows", "hourly": 0.0832, "vcpu": 2, "mem": 4.0},
        {"region": "eastus", "instance_type": "Standard_D2s_v3", "os": "Windows", "hourly": 0.192, "vcpu": 2, "mem": 8.0},
        # West US 2
        {"region": "westus2", "instance_type": "Standard_B1s", "os": "Linux", "hourly": 0.0104, "vcpu": 1, "mem": 1.0},
        {"region": "westus2", "instance_type": "Standard_D2s_v3", "os": "Linux", "hourly": 0.096, "vcpu": 2, "mem": 8.0},
        # West Europe
        {"region": "westeurope", "instance_type": "Standard_B1s", "os": "Linux", "hourly": 0.0114, "vcpu": 1, "mem": 1.0},
        {"region": "westeurope", "instance_type": "Standard_D2s_v3", "os": "Linux", "hourly": 0.107, "vcpu": 2, "mem": 8.0},
        # Southeast Asia
        {"region": "southeastasia", "instance_type": "Standard_B1s", "os": "Linux", "hourly": 0.0116, "vcpu": 1, "mem": 1.0},
        {"region": "southeastasia", "instance_type": "Standard_D2s_v3", "os": "Linux", "hourly": 0.112, "vcpu": 2, "mem": 8.0},
        # Central India
        {"region": "centralindia", "instance_type": "Standard_B1s", "os": "Linux", "hourly": 0.0104, "vcpu": 1, "mem": 1.0},
        {"region": "centralindia", "instance_type": "Standard_D2s_v3", "os": "Linux", "hourly": 0.096, "vcpu": 2, "mem": 8.0},
    ]


def get_azure_storage_data():
    """Azure storage pricing fallback"""
    return [
        {"region": "eastus", "type": "object", "name": "Blob Storage LRS", "price_gb_month": 0.018},
        {"region": "eastus", "type": "block", "name": "Managed Disk P10 LRS", "price_gb_month": 0.095},
        {"region": "westus2", "type": "object", "name": "Blob Storage LRS", "price_gb_month": 0.018},
        {"region": "westus2", "type": "block", "name": "Managed Disk P10 LRS", "price_gb_month": 0.095},
        {"region": "westeurope", "type": "object", "name": "Blob Storage LRS", "price_gb_month": 0.019},
        {"region": "westeurope", "type": "block", "name": "Managed Disk P10 LRS", "price_gb_month": 0.105},
        {"region": "southeastasia", "type": "object", "name": "Blob Storage LRS", "price_gb_month": 0.020},
        {"region": "southeastasia", "type": "block", "name": "Managed Disk P10 LRS", "price_gb_month": 0.110},
        {"region": "centralindia", "type": "object", "name": "Blob Storage LRS", "price_gb_month": 0.018},
        {"region": "centralindia", "type": "block", "name": "Managed Disk P10 LRS", "price_gb_month": 0.095},
    ]


def get_azure_reserved_data():
    """Azure reserved instance pricing fallback"""
    return [
        {"region": "eastus", "instance": "Standard_D2s_v3", "os": "Linux", "term": "one_yr", "payment": "no_upfront", "upfront": 0, "monthly": 42.00, "eff_hourly": 0.058, "savings": 40.0},
        {"region": "eastus", "instance": "Standard_D2s_v3", "os": "Linux", "term": "one_yr", "payment": "all_upfront", "upfront": 504, "monthly": 0, "eff_hourly": 0.057, "savings": 41.0},
        {"region": "eastus", "instance": "Standard_D2s_v3", "os": "Linux", "term": "three_yr", "payment": "all_upfront", "upfront": 840, "monthly": 0, "eff_hourly": 0.032, "savings": 67.0},
    ]


def get_gcp_compute_data():
    """GCP compute pricing fallback (us-east1, Linux)"""
    return [
        {"region": "us-east1", "instance_type": "e2-micro", "os": "Linux", "hourly": 0.0076, "vcpu": 2, "mem": 1.0},
        {"region": "us-east1", "instance_type": "e2-small", "os": "Linux", "hourly": 0.0152, "vcpu": 2, "mem": 2.0},
        {"region": "us-east1", "instance_type": "e2-medium", "os": "Linux", "hourly": 0.0335, "vcpu": 2, "mem": 4.0},
        {"region": "us-east1", "instance_type": "e2-standard-2", "os": "Linux", "hourly": 0.0670, "vcpu": 2, "mem": 8.0},
        {"region": "us-east1", "instance_type": "e2-standard-4", "os": "Linux", "hourly": 0.1340, "vcpu": 4, "mem": 16.0},
        {"region": "us-east1", "instance_type": "e2-standard-8", "os": "Linux", "hourly": 0.2680, "vcpu": 8, "mem": 32.0},
        {"region": "us-east1", "instance_type": "n2-standard-2", "os": "Linux", "hourly": 0.0971, "vcpu": 2, "mem": 8.0},
        {"region": "us-east1", "instance_type": "n2-standard-4", "os": "Linux", "hourly": 0.1942, "vcpu": 4, "mem": 16.0},
        {"region": "us-east1", "instance_type": "c2-standard-4", "os": "Linux", "hourly": 0.2088, "vcpu": 4, "mem": 16.0},
        # Windows
        {"region": "us-east1", "instance_type": "e2-medium", "os": "Windows", "hourly": 0.0670, "vcpu": 2, "mem": 4.0},
        {"region": "us-east1", "instance_type": "n2-standard-2", "os": "Windows", "hourly": 0.1942, "vcpu": 2, "mem": 8.0},
        # US West (Oregon)
        {"region": "us-west1", "instance_type": "e2-micro", "os": "Linux", "hourly": 0.0076, "vcpu": 2, "mem": 1.0},
        {"region": "us-west1", "instance_type": "e2-standard-2", "os": "Linux", "hourly": 0.0670, "vcpu": 2, "mem": 8.0},
        # Europe West (Belgium)
        {"region": "europe-west1", "instance_type": "e2-micro", "os": "Linux", "hourly": 0.0083, "vcpu": 2, "mem": 1.0},
        {"region": "europe-west1", "instance_type": "e2-standard-2", "os": "Linux", "hourly": 0.0737, "vcpu": 2, "mem": 8.0},
        # Asia South (Mumbai)
        {"region": "asia-south1", "instance_type": "e2-micro", "os": "Linux", "hourly": 0.0082, "vcpu": 2, "mem": 1.0},
        {"region": "asia-south1", "instance_type": "e2-standard-2", "os": "Linux", "hourly": 0.0729, "vcpu": 2, "mem": 8.0},
        # Asia Southeast (Singapore)
        {"region": "asia-southeast1", "instance_type": "e2-micro", "os": "Linux", "hourly": 0.0085, "vcpu": 2, "mem": 1.0},
        {"region": "asia-southeast1", "instance_type": "e2-standard-2", "os": "Linux", "hourly": 0.0759, "vcpu": 2, "mem": 8.0},
    ]


def get_gcp_storage_data():
    """GCP storage pricing fallback"""
    return [
        {"region": "us-east1", "type": "object", "name": "Cloud Storage Standard", "price_gb_month": 0.020},
        {"region": "us-east1", "type": "block", "name": "Persistent Disk SSD", "price_gb_month": 0.170},
        {"region": "us-west1", "type": "object", "name": "Cloud Storage Standard", "price_gb_month": 0.020},
        {"region": "us-west1", "type": "block", "name": "Persistent Disk SSD", "price_gb_month": 0.170},
        {"region": "europe-west1", "type": "object", "name": "Cloud Storage Standard", "price_gb_month": 0.020},
        {"region": "europe-west1", "type": "block", "name": "Persistent Disk SSD", "price_gb_month": 0.187},
        {"region": "asia-south1", "type": "object", "name": "Cloud Storage Standard", "price_gb_month": 0.023},
        {"region": "asia-south1", "type": "block", "name": "Persistent Disk SSD", "price_gb_month": 0.204},
        {"region": "asia-southeast1", "type": "object", "name": "Cloud Storage Standard", "price_gb_month": 0.020},
        {"region": "asia-southeast1", "type": "block", "name": "Persistent Disk SSD", "price_gb_month": 0.187},
    ]


def get_gcp_reserved_data():
    """GCP committed use discounts fallback (1yr/3yr CUDs)"""
    return [
        {"region": "us-east1", "instance": "e2-standard-2", "os": "Linux", "term": "one_yr", "payment": "all_upfront", "upfront": 0, "monthly": 34.75, "eff_hourly": 0.048, "savings": 28.0},
        {"region": "us-east1", "instance": "e2-standard-2", "os": "Linux", "term": "three_yr", "payment": "all_upfront", "upfront": 0, "monthly": 24.80, "eff_hourly": 0.034, "savings": 49.0},
        {"region": "us-east1", "instance": "n2-standard-2", "os": "Linux", "term": "one_yr", "payment": "all_upfront", "upfront": 0, "monthly": 50.40, "eff_hourly": 0.069, "savings": 29.0},
        {"region": "us-east1", "instance": "n2-standard-2", "os": "Linux", "term": "three_yr", "payment": "all_upfront", "upfront": 0, "monthly": 36.00, "eff_hourly": 0.049, "savings": 50.0},
    ]


def get_kubernetes_data():
    """Kubernetes node pricing + cluster fees fallback"""
    return [
        # AWS EKS - cluster fee $73/mo
        {"provider": "AWS", "region": "us-east-1", "node_type": "t3.medium", "vcpu": 2, "mem": 4.0, "hourly": 0.0416, "monthly": 30.37, "cluster_fee": 73.0},
        {"provider": "AWS", "region": "us-east-1", "node_type": "m5.large", "vcpu": 2, "mem": 8.0, "hourly": 0.096, "monthly": 70.08, "cluster_fee": 73.0},
        {"provider": "AWS", "region": "us-west-2", "node_type": "t3.medium", "vcpu": 2, "mem": 4.0, "hourly": 0.0416, "monthly": 30.37, "cluster_fee": 73.0},
        # Azure AKS - cluster fee $0
        {"provider": "Azure", "region": "eastus", "node_type": "Standard_D2s_v3", "vcpu": 2, "mem": 8.0, "hourly": 0.096, "monthly": 70.08, "cluster_fee": 0.0},
        {"provider": "Azure", "region": "eastus", "node_type": "Standard_D4s_v3", "vcpu": 4, "mem": 16.0, "hourly": 0.192, "monthly": 140.16, "cluster_fee": 0.0},
        {"provider": "Azure", "region": "westus2", "node_type": "Standard_D2s_v3", "vcpu": 2, "mem": 8.0, "hourly": 0.096, "monthly": 70.08, "cluster_fee": 0.0},
        # GCP GKE - cluster fee $74/mo
        {"provider": "GCP", "region": "us-east1", "node_type": "e2-standard-2", "vcpu": 2, "mem": 8.0, "hourly": 0.0670, "monthly": 48.91, "cluster_fee": 74.0},
        {"provider": "GCP", "region": "us-east1", "node_type": "n2-standard-2", "vcpu": 2, "mem": 8.0, "hourly": 0.0971, "monthly": 70.88, "cluster_fee": 74.0},
        {"provider": "GCP", "region": "us-west1", "node_type": "e2-standard-2", "vcpu": 2, "mem": 8.0, "hourly": 0.0670, "monthly": 48.91, "cluster_fee": 74.0},
    ]


def get_network_data():
    """Network data transfer pricing fallback"""
    return [
        # AWS
        {"provider": "AWS", "region": "us-east-1", "dest": "internet", "price_gb": 0.09, "free_tier": 1.0},
        {"provider": "AWS", "region": "us-east-1", "dest": "cross_region", "price_gb": 0.02, "free_tier": 0.0},
        {"provider": "AWS", "region": "us-east-1", "dest": "same_region", "price_gb": 0.01, "free_tier": 0.0},
        {"provider": "AWS", "region": "us-west-2", "dest": "internet", "price_gb": 0.09, "free_tier": 1.0},
        {"provider": "AWS", "region": "eu-west-1", "dest": "internet", "price_gb": 0.09, "free_tier": 1.0},
        # Azure
        {"provider": "Azure", "region": "eastus", "dest": "internet", "price_gb": 0.087, "free_tier": 5.0},
        {"provider": "Azure", "region": "eastus", "dest": "cross_region", "price_gb": 0.02, "free_tier": 0.0},
        {"provider": "Azure", "region": "eastus", "dest": "same_region", "price_gb": 0.0, "free_tier": 0.0},
        {"provider": "Azure", "region": "westus2", "dest": "internet", "price_gb": 0.087, "free_tier": 5.0},
        {"provider": "Azure", "region": "westeurope", "dest": "internet", "price_gb": 0.087, "free_tier": 5.0},
        # GCP
        {"provider": "GCP", "region": "us-east1", "dest": "internet", "price_gb": 0.08, "free_tier": 1.0},
        {"provider": "GCP", "region": "us-east1", "dest": "cross_region", "price_gb": 0.01, "free_tier": 0.0},
        {"provider": "GCP", "region": "us-east1", "dest": "same_region", "price_gb": 0.0, "free_tier": 0.0},
        {"provider": "GCP", "region": "us-west1", "dest": "internet", "price_gb": 0.08, "free_tier": 1.0},
        {"provider": "GCP", "region": "europe-west1", "dest": "internet", "price_gb": 0.08, "free_tier": 1.0},
    ]


def get_all_fallback_data():
    """Return all fallback data in one structure."""
    return {
        "aws": {
            "compute": get_aws_compute_data(),
            "storage": get_aws_storage_data(),
            "reserved": get_aws_reserved_data(),
        },
        "azure": {
            "compute": get_azure_compute_data(),
            "storage": get_azure_storage_data(),
            "reserved": get_azure_reserved_data(),
        },
        "gcp": {
            "compute": get_gcp_compute_data(),
            "storage": get_gcp_storage_data(),
            "reserved": get_gcp_reserved_data(),
        },
        "kubernetes": get_kubernetes_data(),
        "network": get_network_data(),
    }
