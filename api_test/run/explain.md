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
		- update_file.py 上传数据到桶
		
```



降噪脚本测试报告生成步骤【本地运行】：

1.修改如下三个文件的路径
data_preparation.py	文件的data_warehouse、csv_path路径

clear_data.sh	清空数据脚本

2. 执行如下代码

```shell
代码1：
lyxx@lyxx-System-Product-Name:/mnt/panjiawei/run$ bash clear_data.sh
[sudo] lyxx 的密码：
sudo: 无法执行 /usr/bin/rm: 参数列表过长
说明：当遇到如上报错，原因是minio库东西太多，无法一键删除，需要手动进去删。

代码2：
lyxx@lyxx-System-Product-Name:/mnt/panjiawei/run$ bash run.sh
说明：如无法一键运行，可单独复制运行
```





confusion_matrix运行方法：

准备：将confusion_matrix文件夹直接拷贝到电脑上，在里面运行

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

   输出结果说明：

   ```
   out:
   balck_error_data_1.csv	黑库失败文件
   gray_error_data_1.csv	灰库失败文件
   info.log	日志
   register_timely_save_file_1.csv	注册跑完后的文件
   test_timely_save_file_1.csv	测试跑完后的文件
   correct.csv	埋点数据信息data_cleaning.sh文件
   ```

   报告文档输出：

   confusion_matrix.py 文件的log_level级别设置为1

   在plog/info.log文件中可看到
