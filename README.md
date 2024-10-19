### spark-study
Spark에 대한 기본적인 이론과 K8S환경에서 Spark Cluster환경을 구성하는 내용이 담긴 레포지토리입니다.  

1. spark-on-docker  
- bitnami에서 제공하는 이미지를 활용하여 docker-compose로 Spark환경 구성한 내용입니다.  
2. spark-on-k8s  
- Kuberbetes 환경 위에서 Spark를 구성한 내용입니다.
  2-1. Kubernetes Cluster 구성  
  2-2. Spark Operator 구성 및 작업 제출  
  2-3. Event Log 설정  
  2-4. Spark History Server 구성  
  2-5. Jupyer Notebook 구성  
  2-6. Jupyter Hub 구성  
3. spark-on-eks  
  - `spark-on-k8s`에서 구성한 내용을 확장하여 AWS EKS에서 Spark 환경을 구성한 내용입니다.