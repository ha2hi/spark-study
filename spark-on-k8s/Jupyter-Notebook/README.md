### 개요
py 파일에 작업을 정의 후 어플리케이션 생성 후에 배포하는 방식은 작업 결과를 확인하기에 번거롭습니다.  
바로 결과에 대한 디버깅을 위해 Jupyter Notebook의 필요성을 느꼈습니다.  
  
Spark에서 배포 모드로 3가지의 모드가 있습니다. 각 모드에 대해서 간략하게 설명하겠습니다.
1. Local Mode
![spark-local-mode](/images/spark-local-mode.webp)  
단일 노드에서 spark-submit을 실행하고 Driver와 Executor가 실행됩니다. 따라서 분산처리가 되지 않습니다.  
간단한 배포 모드이며 주로 테스트 및 디버깅에 사용됩니다.
2. Client Mode
![spark-local-mode](/images/spark-client-mode-1.webp)  
![spark-local-mode](/images/spark-client-mode-2.webp)  
![spark-local-mode](/images/spark-client-mode-3.webp)  
spark-submit과 Driver는 같은 노드(로컬 머신)에서 실행이되고 Executor는 Spark Cluster에서 실행됩니다.  
  

Driver가 로컬에서 Spark Session을 생성 후 Resource Manager는 Application Master를 생성합니다.  
Application Master는 다시 Resource Manager에게 Conatainer 생성을 요청합니다. Conatiner 생성 후 Application Master는 각 컨테이너에 Executor를 실행합니다.  
Executor는 Spark Application이 실행하는 중에 동적으로 추가되거나 제거 될 수 있습니다.  
최종적으로 Executor는 Driver와 직접 통신하게 됩니다.  
  
Client Mode의 단점은 로컬 노드에서 Driver가 생성되기 때문에 로컬 노드에서 종료하거나 문제가 생기는 경우 전체 어플리케이션의 문제가 발생합니다.  
  
클라이언트(로컬, spark-submit)하는 환경에서 어플리케이션의 출력 및 로그에 직접 액세스 할 수 있기 때문에 디버깅 및 문제 해결에 도움이 될 수 있습니다.  
3. Cluster Mode
![spark-local-mode](/images/spark-cluster-mode.webp)  
Client 환경은 spark-submit하는 환경(클라이언트)과 Driver환경이 같았다면, Cluster Mode는 Driver 환경이 Spark Cluster에서 실행됩니다.  
spark-submit(Client)환경이 문제가 있다고 어플리케이션에 영향을 미치지 않기 때문에 Production 환경에 적합합니다.  
  

다시 돌아와 우리는 Jupyer에서 Spark를 실행하고 싶어합니다. 그럼 클라이언트(Jupyer)에서 Executor와 바로 통신이 필요하기 때문에 Client 모드를 사용해야 합니다.  
  
spark-subimt, Spark Drive 그리고 Jupyter Notebook의 역할을 하는 Pod를 생성하고 그 Pod는 Spark Operator에 작업을 제출하여 Executor와 통신하게 될 것 입니다.  
  
[목차]
1. Dockerfile과 Image 생성
2. Jupyter 배포
3. 실행
### 참고
https://medium.com/@sephinreji98/understanding-spark-cluster-modes-client-vs-cluster-vs-local-d3c41ea96073 