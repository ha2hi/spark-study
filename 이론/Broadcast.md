Spark에서는 여러 Executor가 전역으로 사용할 수 있는 변수를 설정할 수 있다.  
  
### 1. 브로드캐스트(Broadcast) 변수
브로드캐스트 변수는 모든 Executor에 읽기 전용으로 공유된 변수다.  
여러 Executor에서 작은 크기의 공통된 데이터를 사용해야될 때 사용하면 좋다.  
  
만약 일반 변수로 사용하는 경우 각 태스크마다 데이터를 중복 전송해야되기 때문에 비효율적임.  
```
broadcast_dict = sc.broadcast({"A": 1, "B": 2, "C": 3})
data = sc.parallelize(["A", "B", "D"])

result = data.map(lambda x: broadcast_dict.value.get(x, 0)).collect()
print(result)  # [1, 2, 0]
```  

Ref:  
- https://spark.apache.org/docs/latest/api/python/reference/api/pyspark.Broadcast.html  
