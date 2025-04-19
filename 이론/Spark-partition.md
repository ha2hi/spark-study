## 파티션(Partition)
Spark에서 최소 연산을 Task라고 하는데 하나의 Task는 하나의 Partition에서 실행됩니다. 즉, Partition 단위로 Task들이 여러 노드에서 분산처리합니다.  
또한 하나의 Task는 하나의 Core가 처리합니다. 따라서 `1 Partition = 1 Task = 1 Core`입니다.  
그리고 Patition의 크기는 수가 많을 수록 작고 수가 작을 수록 큽니다.  
  
파티션 많으면 여러 노드에 분산 처리 되기 때문에 많으면 많을 수록(파티션 크기가 작을 수록) 좋을까요?  
아닙니다. 파티션 간의 셔플로 인해 I/O가 많이 발샐하고, 파일 저장 시 Small File Problem이 발생하기 때문에 Disk I/O 비용이 증가합니다.  
  
그렇다면 파티션의 수가 적을 수록(파티션의 크기가 클 수록) 좋을까요?  
그것도 아닙니다. 파티션의 수가 적다면 Excecutor의 메모리가 많이 필요하거나, 특정 파티션에만 데이터가 쏠릴 수 있습니다(Data Skew).  
가장 퍼포먼스가 잘 나올 파티션의 수를 지정해줘야 합니다.  

## 파티션의 종류
파티션의 종류는 3가지로 분류할 수 있습니다.  
- input Partition
- Output Partition
- Shuffle Partition

### Input Partition
Input Partition은 처음 파일을 읽을 때 생성하는 Partition입니다. 관련 설정은 `spark.sql.files.maxpartitionBytes`가 있습니다.  
Default 값은 128MB로 읽으려고하는 파일이 128MB보다 크다면 128MB씩 읽습니다. 반대로 128MB보다 작다면 그대로 읽기 때문에 파일 1개당 1 파티션이 처리합니다.  
대부분의 경우 파일에서 특정 컬럼만 사용하기 때문에 파일 1개당 128MB보다 작습니다.  

### Output Partition
Output Partition은 파일을 저장할 때 생성하는 Partition입니다. 관련 설정은 `df.repartition(cnt), df.coalesce(cnt)`가 있습니다.  
보통 파일 1개의 크기를 HDFS Blocksize(256MB)에 맞춰 설정한는 것이 좋습니다.  

### Shuffle Partition
Spark의 성능에 가장 크게 영향을 미치는 Partition입니다. Join, Group By과 같은 Shuffle 작업에서 생성하는 Partition입니다. 관련 설정은 `spark.sql.shuffle.partition` 입니다.  
Shuffle Partition의 크기는 Shuffle Read Sisze가 100~200MB가 나올 정도로 지정해주는 것이 좋습니다. Shuffle Partition이 커져서 Memory Spill을 방지하기 위해서입니다. 그리고 Core를 최대한 효율적으로 활용하기 위해 Instace * Excecutor Core의 배수로 지정해주는 것이 좋습니다.  

### 최적화
Spark에서 최적화시 쿼리 > Partition 수 > Core 당 메모리 증가 순서대로 확인해봐야합니다.  
쿼리에서 최대한 집계하여 Shuffling을 최소화해야합니다.
