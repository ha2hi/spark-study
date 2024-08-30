### 개요
Spark 2.3에서 기존 Spark Cluster Manager인 Apache Mesos와 Apache Yarn에 이어 추가적으로 Kubernetes는 공식 스케줄러 백엔드가 됐습니다.  
Spark Operator를 사용하면 Spark Application을 선언적 API방식 즉, Yaml파일로 관리할 수 있습니다.  
  
저는 Kubeflow에서 제공하는 Spark Operator를 사용할 것 입니다.  
Spark Operator는 다음과 같은 기능을 제공합니다.  
- Spark 버전 2.3 이상을 지원합니다.
- 사용자 정의 리소스를 통해 선언적 어플리케이션으로 관리합니다.
- 예약된 어플리케이션 실행을 위해 cron을 제공합니다.
- Webhook(웹훅)을 통해 Spark Pod의 사용자 정의를 지원합니다. 예를 들어 ConfigMap 및 Vloumn 마운트와 Pod affinity/anti-affinity가 가능합니다.
  
### Architecture
![spark-oerator](/images/architecture-spark-operator.png)  
1. Spark Application CRD(Customer Resource Definition) 생성 : Spark Application 배포하기 위해 Spark 사용자는 YAML 파일에 Spark Application 구성 정보를 입력하여 실행합니다. 구성 정보에는 Application 이름, 사용할 Spark 이미지, 실행할 메인 클래스, 드라이버 및 익스큐터 리소스 설정등이 포함됩니다.  
2. CRD Controllers 감시 : Controller가 Kubernetes 클러스트이 모든 네임스페이스에서 객체의 생성, 업데이트 및 삭제리를 감시하고 감시한 이벤트에 따라 작동합니다.  
3. 대기열 추가 : SparkApplication이 추가 되면 객체를 내부 작업 대기열에 넣고, 워커가 객체를 선택하여 Submission Runner에게 보냅니다.
4. Application 제출 : Submission Runner가 실제로 Cluster에 실행되도록 어플리케이션을 제출합니다.
5. 작업 종료 : Application 작업이 끝나면 대기열에서 작업이 사라지고, 애플리케이션과 Kubernetes 리소스가 삭제됩니다.

### 작업 목차
1. Helm 설치
2. Spark Operator 설치
3. 실행 및 작업 확인
  
### Helm 설치
Helm을 이용하여 Spark-Operator를 설치할 것 입니다.  

- helm 설치(apt)
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

### Spark Operator 설치 및 계정 생성
Spark Opertor를 설치하기 위해서는 다음과 같이 버전 세팅이 되어 있어야 합니다.
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

- 계정 설정 및 생성
```
kubectl apply -f create_spark_account.yaml

kubectl create clusterrolebinding spark-role --clusterrole=edit --serviceaccount=default:spark --namespace=default
```

### Operator 확인
`kubectl get pods`를 통해 Spark Operator Pod가 Running상태인지 확인해야 됩니다.  

### 실행 및 작업 확인
- 실행
```
kubectl apply -f spark-pi.yaml
```

- 작업 확인
logs에서 spark-pi에 실행한 출력 값인 "Pi is roughly 3.1460557302786514"가 정상적으로 나오는지 확인해야됩니다.  
```
kubectl logs pyspark-pi-driver
```


### 참고
- Kubeflow Spark Operator
  - https://www.kubeflow.org/docs/components/spark-operator/overview/  
- Helm 설치
  - https://helm.sh/ko/docs/intro/install/  
- Spark Operator 설치
  - https://www.kubeflow.org/docs/components/spark-operator/getting-started/  
- 계정 설정
  - https://spark.apache.org/docs/3.1.1/running-on-kubernetes.html