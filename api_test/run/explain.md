```
minio_part
	- os
		- oss_tool.py	os操作模块
	- config.yaml	总配置文件
	- more_run.py	线程式批跑
	- more_run_v2.py	本地多线程跑（需要将所以文件绝对路径保存在文件中）
	- one_file.py	运行单个用例

single_script
	- demand_2.py	自动注册部分2
	- local_sync.py	自动注册部分1
	- confusion_matrix
		- data_preparation.py	数据准备脚本
		- confusion_matrix.py	降噪脚本
		- data_cleaning.sh	一键清空之前的文件
		
```

confusion_matrix运行方法：

1. 运行data_preparation.py文件 

   lyxx@lyxx-System-Product-Name:   python3 data_preparation.py > 2.sh
   lyxx@lyxx-System-Product-Name:   bash 2.sh 【拷贝文件】

   ```
   文件内配置:
   1. 配置数据集路径
   2. 数据集csv路径 (薛之前准备好的)
   	[]speaker_id, wav_number, file_size, speech_duration, gender, channel
   3. 数据保存后的路径
   4. 黑库与灰库数据拷贝的路径
   
   out：
   1. json.json # {wav_name: time}
   2. noblack.txt
   3. zhuanban.txt
   ```

   ​	

2. 运行data_cleaning.sh文件 

   bash data_cleaning.sh

3. 运行confusion_matrix.py文件

   python3 confusion_matrix.py

   ```
   文件内配置：
   1. json.json # {wav_name: time}
   2. noblack.txt
   3. zhuanban.txt
   
   out:
   balck_error_data_1.csv	黑库失败文件
   gray_error_data_1.csv	灰库失败文件
   info.log	日志
   register_timely_save_file_1.csv	注册跑完后的文件
   test_timely_save_file_1.csv	测试跑完后的文件
   TN_1.csv	预测失败信息
   ```

   
