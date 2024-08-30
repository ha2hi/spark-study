### 개요
Spark Operator를 사용하면 driver pod가 종료됨과 동시에 Spark Web UI를 사용할 수 없게 됩니다.  
그리고 작업 로그 저장을 위해 Event Log가 필요합니다. 저장한 Event Log를 History Server를 구성하여 Spark Web UI에서 Spark Job 제출한 결과를 볼 수 있습니다.  
  
Spark Event Log저장 위치는 local(PVC 사용), hdfs, Cloud Storage(S3, GCS)에 저장할 수 있습니다.  
저는 S3에 Event Log 파일을 저장하도록 하겠습니다.  
  
[목차]
1. Secret 생성
2. spark-pi.yaml 파일 수정
3. 작업 제출 및 s3 확인

### 1.Secret 생성
우선 Access Key와 Secret Access Key는 민감 정보이기 때문에 secret을 생성합니다.  
참고로 spark-log-s3-secret.yaml 파일에서 사용하는 액세스키와 비밀액세스키를 입력해야 됩니다.  

```
kubectl apply -f spark-log-secret.yaml
```

### 2.spark-pi.yaml 파일 수정
"Spark Operator 구성 및 작업 제출(Kubeflow-Spark-Operator)"에서 생성한 어플리케이션의 YAML 파일을 수정합니다.  
sparkConf 설정을 추가하고 옵션들을 입력합니다.  
spec.sparkConf.spark.eventLog.dir에 Event Log가 저장될 폴더를 입력합니다.  


### 작업 제출 및 s3 확인
- 작업 제출
이제 Apllication을 실행합니다.  
```
kubectl apply -f spark-pi-event-log.yaml
```

- S3 확인
spark.eventLog.dir로 지정한 폴더에 들어가보면 log가 생성되는걸 볼 수 있습니다.  
![practice-architecture](/images/spark-event-log-history.png) 
저는 작업을 3번 제출했기 때문에 3개의 로그가 쌓인 것 입니다.  


### 참고 
- https://ssup2.github.io/blog-software/docs/theory-analysis/spark-on-kubernetes/