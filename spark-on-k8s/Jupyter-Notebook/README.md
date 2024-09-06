### 개요
py 파일에 작업을 정의 후 어플리케이션 생성 후에 배포하는 방식은 작업 결과를 확인하기에 번거롭습니다.  
바로 결과에 대한 디버깅을 위해 Jupyter Notebook의 필요성을 느꼈습니다.  
  
Spark에서 배포 모드로 3가지의 모드가 있습니다. 각 모드에 대해서 간략하게 설명하겠습니다.
1. Local Mode
![spark-local-mode](/images/spark-local-mode.webp)  
단일 노드에서 spark-submit을 실행하고 Driver와 Executor가 실행됩니다. 따라서 분산처리가 되지 않습니다.  
간단한 배포 모드이며 주로 테스트 및 디버깅에 사용됩니다.

2. Client Mode
![spark-client-mode](/images/spark-client-mode-1.webp)  
![spark-client-mode](/images/spark-client-mode-2.webp)  
![spark-client-mode](/images/spark-client-mode-3.webp)  
spark-submit과 Driver는 같은 노드(로컬 머신)에서 실행이되고 Executor는 Spark Cluster에서 실행됩니다.  
  

Driver가 로컬에서 Spark Session을 생성 후 Resource Manager는 Application Master를 생성합니다.  
Application Master는 다시 Resource Manager에게 Conatainer 생성을 요청합니다. Conatiner 생성 후 Application Master는 각 컨테이너에 Executor를 실행합니다.  
Executor는 Spark Application이 실행하는 중에 동적으로 추가되거나 제거 될 수 있습니다.  
최종적으로 Executor는 Driver와 직접 통신하게 됩니다.  
  
Client Mode의 단점은 로컬 노드에서 Driver가 생성되기 때문에 로컬 노드에서 종료하거나 문제가 생기는 경우 전체 어플리케이션의 문제가 발생합니다.  
  
클라이언트(로컬, spark-submit)하는 환경에서 어플리케이션의 출력 및 로그에 직접 액세스 할 수 있기 때문에 디버깅 및 문제 해결에 도움이 될 수 있습니다.

3. Cluster Mode
![spark-cluster-mode](/images/spark-cluster-mode.webp)  
Client 환경은 spark-submit하는 환경(클라이언트)과 Driver환경이 같았다면, Cluster Mode는 Driver 환경이 Spark Cluster에서 실행됩니다.  
spark-submit(Client)환경이 문제가 있다고 어플리케이션에 영향을 미치지 않기 때문에 Production 환경에 적합합니다.  
  

다시 돌아와 우리는 Jupyer에서 Spark를 실행하고 싶어합니다. 그럼 클라이언트(Jupyer)에서 Executor와 바로 통신이 필요하기 때문에 Client 모드를 사용해야 합니다.  
  
spark-subimt, Spark Drive 그리고 Jupyter Notebook의 역할을 하는 Pod를 생성하고 그 Pod는 Spark Operator에 작업을 제출하여 Executor와 통신하게 될 것 입니다.  
  
[목차]
1. Dockerfile과 Image 생성
2. Jupyter 배포
3. Executor 실행 및 확인

### 1.Dockerfile 생성 및 Image 생성
*주의*  
Dockerfile을 생성하기 앞서 Driver와 Executor의 Python 버전과 Spark 버전은 일치해야 합니다.  
  
- 사용할 이미지
Driver(Jupyer Notebook)과 Executor이미지는 둘 다 공식 이미지를 사용하려고 합니다.  
    - https://hub.docker.com/r/jupyter/scipy-notebook
    - https://hub.docker.com/r/apache/spark/

이 글을 작성하기 전에 공식 이미지를 그대로 배포하고 테스트 해봤습니다.  
Driver와 Executor의 Spark 버전과 Python 버전은 동일해야된다는 에러가 발생하여 확인해보니 Driver의 Python 버전은 3.11, Spark 버전은 3.5.2이었고 Executor의 Python 버전은 3.8, Spark 버전은 3.5.0이었습니다.  
그래서 Jupyter(Driver)의 이미지를 Custom하여 Python 버전은 3.8, Spark 버전은 3.5.0으로 이미지를 생성해야겠다는 생각이 들었습니다.  
  
우선 Python 3.8로 설치하는 과정부터 보겠습니다.   
Jupyter의 pyspark-notebook에서 기본 이미지의 Dockerfile을 확인해보니 여러 이미지와 연결 되어 있다는걸 알게되었습니다.  
jupyter/pyspark-notebook > jupyter/scipy-notebook > jupyter/minimal-notebook > jupyter/base-notebook > jupyter/docker-stacks-foundation  
이미지를 타고 타고 가보니 Python Version이 3.11버전으로 고정되어 있다는걸 알게됐습니다.  
![jupyter-python-image-1](/images/jupyter-python-image-1.png)  
  
막막했던 순간 Github Issues에 나와 같은 문제를 겪고 있던 사람은 없을까하여 Github Issues에 보니 파이썬 버전관련하여 질문을 한 사람이 있었습니다. 댓글에 공식 이미지에 태그로 파이썬 버전이 구분되어 있다는걸 알게됐습니다.
![jupyter-python-image-2](/images/jupyter-python-image-2.png)  
  
Python 버전 문제는 해결했으니 Spark 버전을 맞추는 작업이 필요했습니다.  
Github에서 jupyter/pyspark-notebook의 Dockerfile을 확인해봤습니다.  
![jupyter-python-image-3](/images/jupyter-python-image-3.png) 
아! jupyte/scipy-notebook를 Base Image로 사용하고 Spark를 설치하는구나라는걸 알게됐습니다.  
그런데 Spark Download URL("https://dlcdn.apache.org/spark/")에 가보니 `spark-3.4.3`과 `spark-3.5.2` 버전 밖에 없었습니다.  
  
그냥 jupyte/scipy-notebook를 Base Image로 사용하고 Spark-3.5.0을 설치하는 Custom Image를 생성해야겠다는 생각이 들어 Dockerfile을 생성했습니다.  
Dockerfile을 생성할 때 다음 링크들을 참고했습니다.  
1. https://github.com/jupyter/docker-stacks/blob/main/images/pyspark-notebook/Dockerfile
2. https://gist.github.com/ruslanmv/9518aa1113c48a9002266f7bd3b012a0#file-dockerfile

- Docker Image 생성
```
docker build -t hiha2/pyspark-notebook:spark3.5-python3.8 .

docker push hiha2/pyspark-notebook:spark3.5-python3.8
```
### 2.Jupyter 배포
이미지를 생성했으면 pod를 배포하는건 간단할 것 입니다.
- Jupyter Deploy, Service 배포
```
kubectl apply -f pyspark-jupyter-app.yaml
```

### Executor 실행 및 확인
웹 브라우저에 `<K8s Cluster IP>:30088`로 접속 합니다.  
Token은 `kubectl logs <POD 명>`으로 알 수 있습니다.  
  
노트북을 생성한 후 해당 코드를 실행해봅니다.
```
import os
from pyspark.sql import SparkSession

spark = (
    SparkSession.builder.appName("JupyterApp")
    .master("k8s://https://kubernetes.default.svc.cluster.local:443")
    .config("spark.submit.deployMode", "client")
    .config("spark.executor.instances", "1")
    .config("spark.executor.memory", "1G")
    .config("spark.driver.memory", "1G")
    .config("spark.executor.cores", "1")
    .config("spark.kubernetes.namespace", "default")
    .config(
        "spark.kubernetes.container.image", "apache/spark:3.5.0"
    )
    .config("spark.kubernetes.authenticate.driver.serviceAccountName", "spark")
    .config("spark.kubernetes.driver.pod.name", os.environ["HOSTNAME"])
    .config("spark.driver.bindAddress", "0.0.0.0")
    .config("spark.driver.host", "jupyter-headless.default.svc.cluster.local")
    .getOrCreate()
)
```
Spark Context를 Jupyter Notebook에서 생성한 후 다시 Kubernetes로 돌아와서 `kubectl get pods`를 실행해봅니다.  
![jupyter-python-exec-1](/images/jupyter-python-exec-1.png)  
Executor가 생성되었다는걸 볼 수 있습니다. Spark Mode에서 Client Mode를 설명했었는데 이 때 Executor는 Driver와 직접적으로 통신한다고 말했었습니다.  
실습을 통해 Client Mode가 직접적으로 와닿을 수 있을 것 같습니다.  
  
이제 다음 코드를 실행하여 정상적으로 pyspark작동하는지 확인해 볼 수 있습니다.
```
df = spark.createDataFrame(
    [
        ("sue", 32),
        ("li", 3),
        ("bob", 75),
        ("heo", 13),
    ],
    ["first_name", "age"],
)
df.show()
```
![jupyter-python-exec-2](/images/jupyter-python-exec-2.png)  

### 참고
https://medium.com/@sephinreji98/understanding-spark-cluster-modes-client-vs-cluster-vs-local-d3c41ea96073 