### Spark 기본 상식
- 맵리듀스는 HDFS과 함께 하둡이라고 패키징되어 제공하지만 Spark는 단독  
- Spark가 맵리듀스에 비해 빠른 이유는 메모리 기반 처리와 Lazy Execution 방식
- Spark는 JVM 위에서 실행되면 애플리케이션 실행 시에만 JVM 유지  
- 스파크 애플리케이션의 분산 처리를 원활하게 도와주는 클러스터 매니저를 통해 관리
  - Standalone
  - K8S
  - Hadoop YARN
  - Apache Mesos
  
### RDD 
- RDD는 불변하다.
- RDD의 함수에는 Transformation과 Action이 있다.
  - Transformation은 또 다른 RDD를 Return
  - Action은 RDD가 아닌 것들을 Return
- RDD는 어플리케이션간의 공유가 안되기 때문에 Join과 같은 여러 RDD를 쓰는 경우 동일한 SparkContext를 가져야 한다.

### Job
- Job은 Spark 실행 구성에서 가장 높은 단계
- Job은 1개의 Action에 대응
  - Action은 여러 개의 Transformation을 가짐
  
### 스테이지
- 스테이지는 병렬 연산의 한 단위다.
- 여러 Task들로 구성
- 셔플을 요구하는 경우 스테이지는 분리됨
  - 예를 들어 map, flatmap과 같은 함수는 셔플을 요구하지 않기 때문에 1개의 Stage에서 작업함

### Task
- Task는 실행 단계에서 가장 작은 단위