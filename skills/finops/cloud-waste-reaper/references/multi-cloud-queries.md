# 🔍 Multi-Cloud Waste Detection CLI Commands

This reference provides audited, read-only query commands to identify idle and unattached cloud resources across AWS, Google Cloud Platform (GCP), and Microsoft Azure.

---

## 1. Amazon Web Services (AWS CLI)

### Unattached EBS Volumes
```bash
aws ec2 describe-volumes \
  --filters Name=status,Values=available \
  --query "Volumes[*].{ID:VolumeId,SizeGB:Size,Type:VolumeType,Created:CreateTime,Tags:Tags}" \
  --output table
```

### Unassociated Elastic IP Addresses (EIPs)
```bash
aws ec2 describe-addresses \
  --filters Name=association-id,Values=null \
  --query "Addresses[*].{PublicIP:PublicIp,AllocationId:AllocationId,NetworkBorderGroup:NetworkBorderGroup}" \
  --output table
```

### Abandoned NAT Gateways (Available but potentially idle)
```bash
aws ec2 describe-nat-gateways \
  --filter "Name=state,Values=available" \
  --query "NatGateways[*].{NatGatewayId:NatGatewayId,VpcId:VpcId,SubnetId:SubnetId,Created:CreateTime}" \
  --output table
```

### Empty Application Load Balancers (0 Target Registrations)
```bash
aws elbv2 describe-load-balancers \
  --query "LoadBalancers[?Type=='application'].{ARN:LoadBalancerArn,DNS:DNSName,VPC:VpcId}" \
  --output table
```

---

## 2. Google Cloud Platform (gcloud CLI)

### Unattached Persistent Disks
```bash
gcloud compute disks list \
  --filter="-users:*" \
  --format="table(name,zone,sizeGb,type,status)"
```

### Unassociated Static External IP Addresses
```bash
gcloud compute addresses list \
  --filter="status=RESERVED AND -users:*" \
  --format="table(name,region,address,status)"
```

### Idle Cloud NAT Gateways
```bash
gcloud compute routers nats list \
  --router=ROUTER_NAME \
  --region=REGION \
  --format="table(name,type,natIpAllocateOption)"
```

---

## 3. Microsoft Azure (Azure CLI `az`)

### Unattached Managed OS/Data Disks
```bash
az disk list \
  --query "[?managedBy==null].{Name:name,ResourceGroup:resourceGroup,SizeGB:diskSizeGb,Tier:sku.name}" \
  --output table
```

### Unassociated Public IP Addresses
```bash
az network public-ip list \
  --query "[?ipConfiguration==null].{Name:name,ResourceGroup:resourceGroup,IP:ipAddress}" \
  --output table
```
