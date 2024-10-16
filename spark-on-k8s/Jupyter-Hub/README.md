### 개요
처음에는 Spark Client Mode를 사용하여 Jupyter Notebook에서 Spark를 사용하는 것으로 마무리하려고 했으나, [kubeflow/spark-operator](https://github.com/kubeflow/spark-operator/issues)에서 JupyterHub에서 Spark 사용에 대한 이슈가 이슈가 많이 올라와서 JupyterHub에 대한 궁금함과 한 번 사용해볼겸 구성해보려고 합니다.  

### JupyterHub란?
JupyterHub가 뭔지 그리고 Jupyter Notebook과 무엇이 다른지 알아봅시다.  
JupyterHub란 다중 사용자가 Jupyter Notebook을 이용할 수 있는 환경입니다.  
Notebook 사용자 마다 어떤 사람은 R을 사용하고 싶을 수 있고 또는 Python, Spark 등을 사용하고 싶을 수 있습니다.  
즉 사용자 마다 Notebook 사용 목적이 다릅니다. 이때 JupyterHub를 이용하며 사용자별로 Notebook 환경을 구성할 수 있습니다.  
그리고 사용자 별로 다앙햔 인증 등을 사용할 수 있습니다.  

### K8S 사용 리소스
- [Jupyterhub Helm Conifg](https://github.com/ha2hi/spark-study/blob/main/spark-on-k8s/Jupyter-Hub/config.yaml)
Helm을 사용하여 Jupyterhub를 설치할 때 config.yaml에 구성하고 싶은 환경을 구성할 수 있습니다.  

https://github.com/ha2hi/spark-study/blob/main/spark-on-k8s/Jupyter-Hub/config.yaml#L1-L11


### 1. JupyterHub Helm 설치

```
helm repo add jupyterhub https://hub.jupyter.org/helm-chart/
```