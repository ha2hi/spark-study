## 개요
`spark-on-k8s`에서는 EC2에서 K8S Cluster를 구성하여 Spark를 사용했더라면 해당 리포지토리에서는 AWS EKS에서 Spark를 사용하는 내용을 다룰려고합니다.  
  
EC2가 아닌 EKS에서 Spark를 구성하면 어떤 장점이 있는지 살펴보도록 하겠습니다.

## 아키텍처
저는 EKS에서 Spark환경을 다음과 같이 구성하고자 합니다.
![Spark-on-EKS-architecture](../images/spark-on-eks-arch.png)  
Karpenter, AWS CSI EBS Driver,Graceful Executor Decommissioning 적용 예정입니다.  
  

## 1. API용 EC2 생성
EC2를 생성하여 EKS Cluster에 API를  EC2를 먼저 생성합니다.  
애플리케이션 및 OS 이미지 : Ubuntu Server 24.04 LTS (HVM), SSD Volume Type
인스턴스 유형 : t2.micro
VPC : EKS 클러스터 생성할 VPC
Subnet : 본인의 Pubilc Subnet
- EC2 접속
```
ssh -i <PEM_KEY> ubuntu@<PUBLIC_IP>
```
  
- root 유저로 변경
```
sudo su -
```

- AWS CLI v2 설치
```
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

aws --version
```
  
- eksctl 설치
```
curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
sudo mv /tmp/eksctl /usr/local/bin

eksctl version
```
  
- kubectl 설치
```
curl -o kubectl https://amazon-eks.s3.us-west-2.amazonaws.com/1.19.6/2021-01-05/bin/linux/amd64/kubectl
chmod +x ./kubectl
mkdir -p $HOME/bin && cp ./kubectl $HOME/bin/kubectl && export PATH=$PATH:$HOME/bin
echo 'export PATH=$PATH:$HOME/bin' >> ~/.bashrc

kubectl version --short --client
```
  
- helm 설치
```
curl https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 > get_helm.sh
chmod 700 get_helm.sh
./get_helm.sh
```
  
## 2. EKS Cluster 생성
```
