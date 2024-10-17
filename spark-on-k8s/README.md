### Spark on Kubernetes
많은 기업들에서 Spark 환경을 Kubernetes에서 구성하여 사용하고 있습니다.  
그래서 저도 Kubernetes에 한 번 Spark를 배포할 수 있는 환경을 구성해보면 좋겠다라는 생각이 들어 구성해봤습니다.  
제가 공부한 내용을 공유함으로써 독자분들에게 조금이라도 도움이 되었으면하는 마음으로 작성했습니다.  
  
Spark를 공부할 때 Local Mode로 사용하여 함수 기능을 익혔는데, 문득 기업들은 Spark를 어떻게 구성하면서 사용할까 궁금증이 생겼습니다.  
`엄청 큰 데이터를 처리할 때는 환경을 어떻게 구성하지?`, `로그는 어떻게 관리하지?`, `모니터링은?`, `언제 Client Mode와 Master Mode를 구분하여 사용할까?` 궁금증이 생겨 구성해보게 됐습니다.  
  
"목차"는 계속 수정 및 추가할 예정입니다.  
단순히 Kubernetes Cluster에 Spark 구성하는 것이 끝이 아니라 로그를 위한 History Server 구성, 디버깅을 위한 Jupyter 구성, 모니터링을 위한 Prometheus 구성과 같이 확장하여 작성할 생각입니다.  

### 목차
다음과 같은 순서로 순차적으로 작업을 진행하시면 됩니다.  
1. Kubernetes Cluster 구성(setup-k8s-cluster.md)
2. Spark Operator 구성 및 작업 제출(Kubeflow-Spark-Operator)
3. Event Log 설정(event-log-s3)
4. Spark History Server 구성(history-server)
5. Jupyer Notebook 구성(Jupyter-Notebook)
6. Jupyter Hub 구성(작성중)
7. Github 사용(작성 예정)

### Spark on Kubernetes 장점
왜 많은 기업들은 Spark를 Kubernetes에서 사용하고 있는걸까요?  
1. Spark Cluster Manager관리 용이함
Spark Cluster Manager로는 Yarn, Mesos, Kubernetes가 있습니다. Cluster Manager의 역할은 간단하게 말하면 리소스를 관리하고, Task를 배치하는 역할을 합니다.  
여기서 대부분은 Apache Yarn을 사용하는데, Yarn관리가 생각보다 쉽지 않고 장애가 발생하면 대응하기가 까다롭습니다. 반면 Kubernetes는 여러 팀에서 사용하기 때문에 장애 발생시 도움 요청이 가능합니다.
2. 유연한 리소스 관리
Spark 작업을 Kubernetes에 제출하면, Kubernetes는 사용 가능한 클러스터 자원에 따라 작업을 자동으로 배포하고 관리합니다. 이를 통해 리소스의 과도한 사용을 방지하고, 자원의 활용도를 극대화할 수 있습니다.
3. 모니터링 및 로깅
Kubernetes는 모니터링 및 로깅과 관련하여 다양한 생태계를 구축한 상태입니다. Prometheus, Grafana, S3등을 사용하여 Spark의 작업 상태를 모니터링 하고 로그를 분석할 수 있습니다.  
이외에도 다양한 장점이 있습니다.  
그리고 단점 또한 있습니다. 기존에 Kubernetes를 사용하고 있지 않다고하면 Cluster를 구성해야 된다는 단점이 있고, 컨테이너에 대해서 어느정도 알고 있어야 합니다.  

### 실습 아키텍처
![practice-architecture](/images/practice-architecture.png)  
Spark Job을 제출하는 방법은 spark-submit방식과 Spark Operator를 이용하는 방식이 있습니다. 저는 Spark Operator를 이용하여 작업을 제출하는 방법을 이용하려고합니다.  
spark-submit방식은 내가 직접 CLI를 통해 spark-submit하는 반면에 Spark Operator방식은 Operator Deployment를 먼저 실행한 후 YAML로 Kubernetes Application Object를 정의하고 배포하면 Spark Operator 내부에서 spark-submit을 통해 작업을 제출합니다.  
  
작업을 수행한 로그를 S3에 저장할 것이고, 저장된 S3 로그를 볼 수 있는 Spark History Server를 구성할 것 입니다.  

### 에러 발생시 참고(디버깅)
저도 우여곡절 끝에 구성했습니다.  
구성 과정 중에 다양한 이유로 구성하는 과정에서 에러가 발생할 것 입니다.  
이 때 로그를 보면서 구글링하면 해결할 수 있을 것 입니다.  
`kubectl logs <pod명>`, `kubectl describe pod <pod명>`를 적극적으로 활용하시면 좋습니다.  
  
외에도 댓글 혹은 제 개인 메일로 안되는 부분 말씀해주시면 답변드리겠습니다.  

### 예상 비용
테스트를 위한 K8S를 위한 EC2 구성 정보는 다음과 같습니다.  
[환경]  
|서버명|OS|인스턴스타입|스토리지구성|
|------|---|---|---|
|k8s-master|Ubuntu22.04 LTS|t2.xlarge|100GB gp2|
|k8s-node1|Ubuntu22.04 LTS|t2.xlarge|100GB gp2|
|k8s-node2|Ubuntu22.04 LTS|t2.xlarge|100GB gp2|
  
예상 비용은 10시간 사용 기준 ((3*$0.23) + (3*$0.11))*10 = $10.2(14,000원)입니다.  
※ 서울 리전 기준 t2.xalrge 비용은 시간당 $0.23, EBS는 100GB GP2 1개당 $0.11입니다.  

### 참고하면 좋은 링크
- https://github.com/apache/spark/blob/master/docs/running-on-kubernetes.md