## 개요
처음에는 Spark Client Mode를 사용하여 Jupyter Notebook에서 Spark를 사용하는 것으로 마무리하려고 했으나, [kubeflow/spark-operator](https://github.com/kubeflow/spark-operator/issues)에서 JupyterHub에서 Spark 사용에 대한 이슈가 이슈가 많이 올라와서 JupyterHub에 대한 궁금함과 한 번 사용해볼겸 구성해보려고 합니다.  

## JupyterHub란?
JupyterHub가 뭔지 그리고 Jupyter Notebook과 무엇이 다른지 알아봅시다.  
JupyterHub란 다중 사용자가 Jupyter Notebook을 이용할 수 있는 환경입니다.  
Notebook 사용자 마다 어떤 사람은 R을 사용하고 싶을 수 있고 또는 Python, Spark 등을 사용하고 싶을 수 있습니다.  
즉 사용자 마다 Notebook 사용 목적이 다릅니다. 이때 JupyterHub를 이용하며 사용자별로 Notebook 환경을 구성할 수 있습니다.  
그리고 사용자 별로 다앙햔 인증 등을 사용할 수 있습니다.  

## K8S 사용 리소스
### [Jupyterhub Helm Conifg](https://github.com/ha2hi/spark-study/blob/main/spark-on-k8s/Jupyter-Hub/config.yaml)  
Helm을 사용하여 Jupyterhub를 설치할 때 config.yaml에 구성하고 싶은 환경을 구성할 수 있습니다.  
- hub
  - config.Authenticator.admin_users[] : User 설정
  - config.DummyAuthenticator.password : PW 설정
  - JupyterHub.authenticator_class : 사용자 인증방식으로 모든 User의 패스워드를 DummyAuthenticator.password에서 설정한 값으로 지정
- singleuser
  - nodeSelector.kubernetes.io/hostname : Hub를 배포할 Node IP 입력
  - profileList: 저는 2개의 환경을 생성했습니다. (Storage Class 분리)
  - Spark 이미지는 이전에 [Jupyter-Notebook](https://github.com/ha2hi/spark-study/blob/main/spark-on-k8s/Jupyter-Notebook/Dockerfile)구성 당시 사용한 이미지를 그대로 사용했습니다.
- proxy.service.type : NodePort, 설정 안하면 LB Type으로 SVC가 생성됩니다.  

### [RBAC](https://github.com/ha2hi/spark-study/blob/main/spark-on-k8s/Jupyter-Hub/spark-rbac.yaml)
`config.yaml` 파일에서 `singleuser.serviceAccountName: spark` 지정한 RBAC입니다.  

### [Storage Class](https://github.com/ha2hi/spark-study/blob/main/spark-on-k8s/Jupyter-Hub/sc.yaml)
`config.yaml`에서 Python과 Spark 환경의 Storage Class를 각각 구성되게 만들었습니다.  
  
### Persistent Volumes
[python-pv](https://github.com/ha2hi/spark-study/blob/main/spark-on-k8s/Jupyter-Hub/python-pv.yaml), [spark-pv](https://github.com/ha2hi/spark-study/blob/main/spark-on-k8s/Jupyter-Hub/spark-pv.yaml)
  
### [Service](https://github.com/ha2hi/spark-study/blob/main/spark-on-k8s/Jupyter-Hub/headless-service.yaml)
Spark Clint Mode를 사용하기 위해 headless-service를 구성했습니다.

## 작업
### 1. 사용 리소스 실행
- ServiceAccount 생성 및 롤바인딩
```
kubectl apply -f spark-rbac.yaml
```
  
- Storage Class 생성
```
kubectl apply -f sc.yaml
```
  
- PV 생성
```
kubectl apply -f python-pv.yaml

kubectl apply -f spark-pv.yaml
```
  
- Service 생성
```
kubectl apply -f headless-service.yaml
```

### 2. JupyterHub 서버 실행
저는 `jupyterhub` 네임스페이스에 Hub를 구성했습니다.  
```
helm upgrade --cleanup-on-fail \
  --install jupyterhub jupyterhub/jupyterhub \
  --namespace jupyterhub \
  --create-namespace \
  --values config.yaml
```
`hub`와 `proxy` Pod가 정상적으로 실행되고 있는지 확인합니다.