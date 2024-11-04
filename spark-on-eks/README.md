## 개요
`spark-on-k8s`에서는 EC2에서 K8S Cluster를 구성하여 Spark를 사용했더라면 해당 리포지토리에서는 AWS EKS에서 Spark를 사용하는 내용을 다룰려고합니다.  
  
EC2가 아닌 EKS에서 Spark를 구성하면 어떤 장점이 있는지 살펴보도록 하겠습니다.

## 아키텍처(초안)
저는 EKS에서 Spark환경을 다음과 같이 구성하고자 합니다.
![Spark-on-EKS-architecture](../images/spark-on-eks-arch.png)  
적용 예정  
1. AWS CSI EBS Driver(o)
2. Karpenter
3. Graceful Executor Decommissioning
  

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
  
- docker 서ㄹ치
```
yum install docker -y

sudo service docker start
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
  
## 2. EKS Cluster 생성 및 EBS CSI Driver 구성
- EKS Cluster 생성
대략 30분가량 걸립니다.
```
kubectl apply -f eks-cluster.yaml
```
  
- Role 확인
```
eksctl get iamserviceaccount --cluster spark-on-eks
```
  
- aws-ebs-csi-driver 설치
```
eksctl create addon --name aws-ebs-csi-driver --cluster spark-on-eks --service-account-role-arn  <ebs-csi-controller-sa Role> --force
```
  
- Addon 설치 확인
```
eksctl get addon --cluster spark-on-eks
```
  
- csinode 확인
```
kubectl get csinodes
```
  
## 3. AWS ECR Repository 구성
쿠버네티스에 Pod를 배포할 때 Image 정보를 확인하여 DockerHub와 같은 이미지 저장소에서 Image를 설치하여 Pod에 배포합니다.  
- Public Registry 인증
```
aws ecr-public get-login-password \
  --region us-east-1 | docker login --username AWS \
  --password-stdin public.ecr.aws
```
![Registry 인증](../images/spark-on-eks-4.png)  
  
- Public Repository 생성
`aws ecr-public create-repository --repository-name <레포지토리 명> --region us-east-1`
```
# Jupyterhub
aws ecr-public create-repository --repository-name spark-study/jupyterhub --region us-east-1

# Prometheus
aws ecr-public create-repository --repository-name spark-study/prometheus --region us-east-1
```
  
- Repository URL 확인
생성한 `spark-repo/spark` Repository의 Uri를 확인합니다.  
해당 Uri에 이미지를 Pull/Push할 것 입니다.  
```
# Jupyterhub URL
aws ecr-public describe-repositories --region us-east-1 | jq -r '.repositories[] | select(.repositoryName == "spark-study/jupyterhub") | .repositoryUri'

# Prometheus URL
aws ecr-public describe-repositories --region us-east-1 | jq -r '.repositories[] | select(.repositoryName == "spark-study/prometheus") | .repositoryUri'
```
  
- Spark 이미지 생성
JupyterHub에서 사용할 Spark 이미지와 Prometheus에서 사용할 이미지를 생성합니다.  
```
# JupyterHub 이미지
docker build -t public.ecr.aws/<레지스트리 별칭>/spark-study/jupyterhub -f /jupyterhub/Dockerfile .

# Prometheus에서 이미지
docker build -t public.ecr.aws/<레지스트리 별칭>/spark-study/prometheus -f /prometheus/Dockerfile .
```

## 3. Jupyterhub 구성
- `jupyterhub` 네임스페이스 생성
Jupyterhub의 자원들(pod, svc, pvc)은 `jupyterhub` 네임스페이스 관리할 것 입니다.   
```
kubectl create ns jupyterhub
```
  
- StorageClass & RBAC 생성
```
kubectl apply -f sc-jupyterhub.yaml

kubectl apply -f spark-rbac.yaml
```
  
- Install Jupyterhub
```
helm repo add jupyterhub https://hub.jupyter.org/helm-chart/

helm repo update

helm upgrade --cleanup-on-fail \
  --install jupyterhub jupyterhub/jupyterhub \
  --namespace jupyterhub \
  --create-namespace \
  --values config.yaml
```
  
- Jupyterhub 설치 확인
```
kubectl get pods -n jupyterhub
```
  
- Jupyterhub 접속
```
# 외부 IP 확인
kubectl get nodes -owide
```
![Jupyterhub 로그인창](../images/spark-on-eks-1.png)  
`spark_user`로 로그인한 후 Spark 환경을 선택 합니다.  
다음과 같이 정상적으로 접속되고 AWS EBS가 생성될 것 입니다.  
![Jupyterhub 노트북 확인](../images/spark-on-eks-2.png)  
![EBS 확인](../images/spark-on-eks-3.png)  

