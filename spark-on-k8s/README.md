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

