### 개요
해당 Kubernetes Cluster 구성은 2024.08.21일 기준으로 Kubernetes kubeamd 설치 Documentation(https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/install-kubeadm/) 버전 1.31 설치 과정입니다.   
kubernetes 설치 Documentation이 수정되어도 Docker설치와 메모리 스왑종료, iptables 설정, cgroup 설정은 동일하기 때문에 참고하고 나머지는 Documentation 가이드에 맞춰 설치하면 될 것 입니다.   
운영체제는 Ubuntu22.04입니다.  
  
처음에는 t2.large로 생성하였으나 Spark 작업 제출시 CPU 리소스 부족 문제가 있어 t2.xlarge로 구성하였습니다.  
  
[환경]  
|서버명|OS|인스턴스타입|
|------|---|---|
|master|Ubuntu22.04|t2.xlarge|
|node1|Ubuntu22.04|t2.xlarge|
|node2|Ubuntu22.04|t2.xlarge|'

[목차]
1. Install Docker
2. Before you begin
3. Install kubeadm, kubelet, kubectl
4. Create Cluster with kubeamd
5. Worker Node join
### 1.Install Docker(master&node)
Kubernetes를 설치하기 앞 서 Docker를 먼저 설치해야 됩니다.  

- 필요 패키지 설치
```
sudo apt-get update
 
sudo apt-get install \
    ca-certificates \
    curl \
    gnupg \
    lsb-release
```

- GPG Key 추가
```
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
```

- Stable repository 설정
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

- Docker 실행 여부 확인
정상적으로 설치가 되었다면 `docker ps` 실행 시 CONTAINER ID, IMAGE, COMMAND, CREATED..로 출력 될 것 입니다.  

```
docker ps
```

### 2. Before you begin(master&node)
kubeadm, kubelet, kubectl를 설치하기 앞 서 메모리 스왑 종료, iptables, 방화벽에 대한 설정이 필요합니다.  

- 메모리 스왑 종료
Kubernetes를 설치하기 위해서는 메모리 스왑을 종료해야 됩니다.  
메모리 스왑은 RAM의 용량이 부족할 때 디스크의 일부 공간을 메모리처럼 사용하는 것을 의미합니다.

```
sudo swapoff -a && sudo sed -i '/swap/s/^/#/' /etc/fstab
```

- iptables에 브릿지 네트워크 설정
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

- 방화벽 비활성
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

```
sudo apt-mark hold kubelet kubeadm kubectl
```

### 4. Create Cluster with kubeamd(Only master)
- kubeadm 연결
```
kubeamd init
```
kubeamd init을 실행하면 하단에 kubeadm join ~~ 문구가 있습니다.  
해당 명령어를 따로 저장해둡니다. (node instance에서 해당 명령어 입력하여 Master와 연결)  
ex)  
`kubeadm join 172.13.5.178:6443 --token hzo8ak.n9p2j1cfm7o1150g \
	--discovery-token-ca-cert-hash sha256:4d179de7`

- kubectl 명령어 사용 설정
```
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
```

- kubectl 명령어 작동 여부 확인
이제 `kubectl get nodes`를 Shell에 입력해보면 Master Node가 NotReady 상태로 출력 될 것 입니다.
```
kubectl get nodes
```

- Pod network 애드온 설치
network 애드온 설치하기 전에 `kubectl get nodes`를 확인해보면 control-plain의 STATUS가 "NotReady"상태였습니다.  
애드온 설치 후 get nodes를 확인해보면 `Ready`상태로 변하는걸 알 수 있습니다.
```
kubectl apply -f https://github.com/weaveworks/weave/releases/download/v2.8.1/weave-daemonset-k8s.yaml
```

### 5. Worker Node join(node)
이제 worker Node를 클러스터에 연결 할 것입니다.  
kubeadm init 명령어 실행 때 kubeamd join~~ 명령문을 저장했었는데 worker Node노드에서 해당 명령어를 실행합니다.
```
kubeadm join 172.13.5.178:6443 --token hzo8ak.n9p2j1cfm7o1150g \
	--discovery-token-ca-cert-hash sha256:4d179de7f6
```

### 6. 확인
master node에서 정상적으로 clustr가 구성되었는지 확인해봅니다.  
3개의 노드의 STATUS가 Ready상태이면 정상적으로 설치된 것 입니다.  
```
kubectl get nodes
```

### 참고
[설치]
- https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/install-kubeadm/  
- https://velog.io/@fill0006/Ubuntu-22.04-%EC%BF%A0%EB%B2%84%EB%84%A4%ED%8B%B0%EC%8A%A4-%EC%84%A4%EC%B9%98%ED%95%98%EA%B8%B0  
  
[이슈]
- https://blusky10.tistory.com/473  
- https://github.com/containerd/containerd/issues/8139  
  


### 이슈 해결 참고
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
