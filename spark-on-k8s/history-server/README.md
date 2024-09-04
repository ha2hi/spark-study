### 개요
지난 번에 Spark Event Log를 S3에 저장했습니다.  
해당 Log를 Spark Web UI에서 확인하기 위해서는 Spark History Server를 구성하여(pod를 생성하여) 볼 수 있습니다.  
  
저는 AWS에서 제공하는 Docker Image를 참고하여 History Server를 구성했습니다.
  
[목차]
1. Docker Image 생성
2. History Server 배포
3. Service(서비스) 배포 및 확인

### 1.Docker Image 
Dokcer Hub에 이미지 Push를 위해 로그인합니다.
- Docker login
```
docker login
```
  
Docker Image를 생성합니다.
- docker Build
```
docker build -t hiha2/spark-history-s3:3.3.0-v0.1 .
```
  
- docker Image 생성 확인
```
docker images
```
  
- Docker Image DockerHub에 Push
```
dcoker push hiha2/spark-history-s3:3.3.0-v0.1
```

### 2.History Server 배포
생성한 이미지를 바탕으로 Deployment로 History Server를 배포합니다.  
이 때 S3 log 저장 위치와 액세스키, 비밀액세스키는 수정하여 입력해야됩니다.  
저는 지난번에 Secret으로 생성했기 때문에 Secret으로 입력했습니다.  

- Deployment 배포
```
kubectl apply -f spark-history-server.yaml
```

### 3.서비스 배포 및 확인
서비스를 배포하여 History Server가 재대로 구성되었는지 확인해보겠습니다.  

- Service 배포
```
kubectl apply -f spark-history-service.yaml
```

- History Server 확인
서비스 배포했으니 웹 브라우저에 `<ec2 IP>:18080`을 입력하여 확인해봅니다.  
S3에 저장된 로그들이 잘 나오면 성공입니다.  
![practice-architecture](/images/spark-history-server-ui.png) 

### 참고
- https://github.com/aws-samples/aws-glue-samples/tree/master/utilities/Spark_UI