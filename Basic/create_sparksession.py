from pyspark.conf import SparkConf
from pyspark.sql import SparkSession

conf = SparkConf().setAll([
    ("spark.executor.instances", "4")                                   # executor 수
    ("spark.executor.memory", "4g"),                                    # executor 메모리
    ("spark.executor.cores", "2"),                                      # executor당 코어 수
    ("spark.driver.memory", "2"),                                       # Driver 메모리
    ("spark.driver.cores", "1"),                                        # Driver 코어
    ("spark.sql.shuffle.partitions", "200"),                            # 파티션 수
    ("spark.memory.fraction", "0.6"),                                   # Spark 메모리 비율
    ("spark.hadoop.fs.s3a.access.key", "YOUR_ACCESS KEY"),              # AWS 액세스 키
    ("spark.hadoop.fs.s3a.secret.key", "YOUR_SECRET_ACCESS KEY"),       # AWS 비밀 액세스 키
    ("spark.eventLog.enabled", "true"),                                 # 이벤트 로그 사용 여부
    ("spark.eventLog.dir", "s3a://BUCKET_NAME/FOLDER_NAME"),            # 이벤트 로그 저장 위치
    ("spark.ui.showConsoleProgress", "true"),                           # 콘솔 진행률 확인
    ("spark.task.maxFailures", "4"),                                    # 작업 실패 시 재시도 횟수   
    ("spark.serializer", "org.apache.spark.serializer.KryoSerializer"), # 직렬화 방식

])

# 세션 생성
spark = SparkSession.builder.config(conf).getOrCreate()

# 세션 종료
# spark.stop()