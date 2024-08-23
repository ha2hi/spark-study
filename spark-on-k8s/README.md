## Kubernetes Cluster 구성(kubeamd)
해당 Cluster 구성은 2024.08.21일기준 docs 기준 v1.31설치 과정입니다.  
kubernetes.io의 install docs가 수정되어도 Docker설치와 메모리 스왑종료, iptables 설정, cgroup 설정은 동일하기 때문에 참고하고 나머지는 docs 가이드에 맞춰 설치하면 됩니다.  
[환경]  
|서버명|OS|인스턴스타입|
|------|---|---|
|master|Ubuntu22.04|t2.large|
|node1|Ubuntu22.04|t2.large|
|node2|Ubuntu22.04|t2.large|
### 1. Install Docker(master&node)
- 필요 패키지 설치(사전준비)
```
sudo apt-get update
 
sudo apt-get install \
    ca-certificates \
    curl \
    gnupg \
    lsb-release
```

- GPG Key 추가(사전준비)
```
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
```

- Stable repository 설정(사전준비)
```
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

- Docker 설치
```
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io
```

- Docker 실행
```
sudo systemctl enable docker
sudo systemctl start docker
```

### 2. Install kubeadm(master&node)
- 메모리 스왑 종료(사전 준비)
메모리 스왑은 RAM의 용량이 부족할 때 디스크의 일부 공간을 메모리처럼 사용하는 것을 의미합니다.  
```
sudo swapoff -a && sudo sed -i '/swap/s/^/#/' /etc/fstab
```

- iptables에 브릿지 네트워크 설정(사전 준비)
노드간 통신을 위해 브릿지 네트워크 설정이 필요합니다.
```
cat <<EOF | sudo tee /etc/modules-load.d/k8s.conf
br_netfilter
EOF
 
cat <<EOF | sudo tee /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
EOF
sudo sysctl --system
```

- 방화벽 비활성(사전 준비)
```
sudo ufw disable
```

### 3. Install kubeadm, kubelet, kubectl(master&node)
- ca관련 패키지 설치
```
sudo apt-get update

sudo apt-get install -y apt-transport-https ca-certificates curl gpg
```

- public signing key 설치
```
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.31/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
```

- apt 저장소 추가
```
echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.31/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list
```

- kubelet, kubeadm, kubectl 설치
```
sudo apt-get update
sudo apt-get install -y kubelet kubeadm kubectl
sudo apt-mark hold kubelet kubeadm kubectl
```

- kubelet 활성화
```
sudo systemctl enable --now kubelet
```

- cgroup 설정
```
cat <<EOF | sudo tee /etc/docker/daemon.json
{
  "exec-opts": ["native.cgroupdriver=systemd"],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m"
  },
  "storage-driver": "overlay2"
}
EOF
```

- 서비스 등록 및 재수행
```
sudo systemctl daemon-reload
sudo systemctl restart kubelet
```

- containerd cgrop 설정
```
rm /etc/containerd/config.toml

containerd config default | tee /etc/containerd/config.toml
sed -i 's/SystemdCgroup = false/SystemdCgroup = true/g' /etc/containerd/config.toml  
service containerd restart
service kubelet restart
```

### 4. Create Cluster with kubeamd(master)
- kubeadm 연결
```
kubeamd init
```
kubeadm join ~~ 문구 저장하기 <-node에서 해당 명령어 입력하여 Master와 연결
`kubeadm join 172.13.5.178:6443 --token hzo8ak.n9p2j1cfm7o1150g \
	--discovery-token-ca-cert-hash sha256:4d179de7f6abc80f1d1d2d674ba43d28de98e00baef6ac01572cc57ea7b5e69c`

- kube 명령어 사용 설정
```
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
```

- The connection to the server 172.13.5.178:6443 was refused - did you specify the right host or port? 에러 해결
```
containerd config default | tee /etc/containerd/config.toml
sed -i 's/SystemdCgroup = false/SystemdCgroup = true/g' /etc/containerd/config.toml  
service containerd restart
service kubelet restart
```

- Pod network 애드온 설치
network 애드온 설치하기 전에 `kubectl get nodes`를 확인해보면 control-plain의 STATUS가 "NotReady"상태이다.  
애드온 설치 후 get nodes를 확인해보면 `Ready`상태로 변하는걸 알 수 있다.
```
kubectl apply -f https://github.com/weaveworks/weave/releases/download/v2.8.1/weave-daemonset-k8s.yaml
```

### 5. Worker Node join(node)
이제 worker Node를 클러스터에 연결 할 것입니다. kubeadm init 명령어 실행 때 kubeamd join~~를 마스터를 제외한 노드에서 실행합니다.
```
kubeadm join 172.13.5.178:6443 --token hzo8ak.n9p2j1cfm7o1150g \
	--discovery-token-ca-cert-hash sha256:4d179de7f6abc80f1d1d2d674ba43d28de98e00baef6ac01572cc57ea7b5e69c 
```

### 6. 확인
master node에서 정상적으로 clustr가 구성되었는지 확인해봅니다.  
3개의 노드의 STATUS가 Ready상태이면 정상적으로 설치된 것 입니다.  
```
kubectl get nodes
```

### 참고
설치 : https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/install-kubeadm/
설치 : https://velog.io/@fill0006/Ubuntu-22.04-%EC%BF%A0%EB%B2%84%EB%84%A4%ED%8B%B0%EC%8A%A4-%EC%84%A4%EC%B9%98%ED%95%98%EA%B8%B0
이슈 : https://blusky10.tistory.com/473
이슈 : https://github.com/containerd/containerd/issues/8139

## helm 설치
### apt를 사용하여 helm 설치
- helm 설치
```
curl https://baltocdn.com/helm/signing.asc | gpg --dearmor | sudo tee /usr/share/keyrings/helm.gpg > /dev/null
sudo apt-get install apt-transport-https --yes
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/helm.gpg] https://baltocdn.com/helm/stable/debian/ all main" | sudo tee /etc/apt/sources.list.d/helm-stable-debian.list
sudo apt-get update
sudo apt-get install helm
```

- helm 버전 확인
```
helm version
```

### 참고
https://helm.sh/ko/docs/intro/install/

## spark operator 
GCP(Kubeflow)에서 제공하는 spark-operator를 설치하고 작업을 summit할 것 입니다.  
링크 : https://www.kubeflow.org/docs/components/spark-operator/getting-started/
- Prerequisites
Helm >= 3
Kubernetes >= 1.16

- add helm repo
```
helm repo add spark-operator https://kubeflow.github.io/spark-operator

helm repo update
```

- install chart
webhook.enable=true를 추가하면 뭐가 달라질까요?  
해당 기능이 활성화된다면 Spark 파드가 생성될 때 `spark-operator`가 해당 파드의 스펙을 동적으로 수정할 수 있습니다.  
배포할 때 request, limit와 같이 요구사항을 동적으로 조정할 수 있습니다.  
```
helm install spark spark-operator/spark-operator \
    --set webhook.enable=true
```

- create service account
vi create_spark_account.yaml
```
apiVersion: v1
kind: ServiceAccount
metadata:
  name: spark
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: spark-cluster-role
rules:
- apiGroups: [""] # "" indicates the core API group
  resources: ["pods"]
  verbs: ["get", "watch", "list", "create", "delete"]
- apiGroups: [""] # "" indicates the core API group
  resources: ["services"]
  verbs: ["get", "create", "delete"]
- apiGroups: [""] # "" indicates the core API group
  resources: ["configmaps"]
  verbs: ["get", "create", "delete"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: spark-cluster-role-binding
subjects:
- kind: ServiceAccount
  name: spark
  namespace: default
roleRef:
  kind: ClusterRole
  name: spark-cluster-role
  apiGroup: rbac.authorization.k8s.io
```
```
kubectl apply -f create_spark_account.yaml
```

- spark-operator deploy 접속
```
kubectl exec -it deploy/spark-spark-operator -- bash
```

- spark-summit
spark-submit시 `--master`에는 k8s://<k8s control-plane Prviate IP>를 입력하면 됩니다.  
`namespace`와 `serviceAccountName` 부분은 각각 helm chart 배포시 설정과 service account 생성시 설정과 맞춰 입력하시면 됩니다.  
```
/opt/spark/bin/spark-submit \
        --master k8s://172.13.5.182:6443 \
        --deploy-mode cluster \
        --driver-cores 1 \
        --driver-memory 512m \
        --num-executors 1 \
        --executor-cores 1 \
        --executor-memory 512m \
        --class org.apache.spark.examples.SparkPi \
        --conf spark.kubernetes.namespace=default \
        --conf spark.kubernetes.container.image=apache/spark:3.5.1 \
        --conf spark.kubernetes.authenticate.driver.serviceAccountName=spark \
        --conf spark.kubernetes.authenticate.caCertFile=/var/run/secrets/kubernetes.io/serviceaccount/ca.crt  \
        --conf spark.kubernetes.authenticate.oauthTokenFile=/var/run/secrets/kubernetes.io/serviceaccount/token  \
        local:///opt/spark/examples/src/main/python/pi.py
```

- 정상 배포 확인
우선 deploy에서 빠져나옵니다.  
```
exit
```
pod 확인
```
kubectl get pods
```
다음과 같이 나오면 정상적으로 실행된 것입니다.
```
NAME                                                        READY   STATUS      RESTARTS   AGE
org-apache-spark-examples-sparkpi-908d85917e6de09f-driver   0/1     Completed   0          34m
pythonpi-ca9e7e917e6df45d-exec-1                            0/1     Completed   0          34m
spark-spark-operator-69b68b6d5b-6vwzz                       1/1     Running     0          129m
```

### 참고
spark-operator 버전이나 여러가지 문제로 그대로 실행하면 안될 수 있습니다.  
잘 안될 시 `kubectl describe pod <파드명>`또는 `kubectl get log <파드명>`로 로그를 확인해봐야됩니다.  



## 이슈
[k8s cluster 구성]
1. k8s CNI 이슈 해결해야됨.(해결 완료)
- 이슈 내용
  - node 연결시 weave가 계속 에러가 발생하여 RESTARTS됨.
- 해결 방법
  - containerd cgroup 설정을 Master Node(control-plane) 뿐만 아니라 Worker Node(Node)도 설정해줘야 된다.
```
rm /etc/containerd/config.toml

containerd config default | tee /etc/containerd/config.toml
sed -i 's/SystemdCgroup = false/SystemdCgroup = true/g' /etc/containerd/config.toml  
service containerd restart
service kubelet restart
```