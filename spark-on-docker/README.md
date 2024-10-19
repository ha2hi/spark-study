### Spark on Docker(bitnami)
- EC2에서 Dokcer 컨테이너를 배포하여 EKS Cluster 구성  
- Bitnami에서 제공하는 이미지를 사용하여 Standalone Mode로 Spark job 배포

### Standalone Mode
Spark에서는 다양한 Mode가 있다. Standalone, Yarn, Kubernetes 등..
- Standalone
  - Spark안에 있는 관리자를 통해 실행하는 방식
- Yarn
  - Yarn이라는 프레임워크를 Cluster Manager로 사용하여 실행하는 방식
  - Yarn을 통해 다양한 Apache Hadoop 생태계와 연결할 수 있다.

### 사전준비
1. Docker 설치
2. Docker-compose 설치

### 작업
1. docker-compose 배포
```
docker-compose up -d
```
2. 파이썬 파일 복사 및 실행
```
cp test.py /spark/ha2hi/test.py
```
3. spark-submit
```
docker exec <Master 컨테이너명> spark-submit --master spark://<IP>:7077 /spark/ha2hi/test.py
```
4. 웹 UI에서 결과 확인
웹 브라우저에 <EC2 Public IP>:8080을 입력한 후 Spark 웹 UI로 정상적으로 작업이 실행됐는지 확인한다.
   