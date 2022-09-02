## 一、 代码规范

1. 模块使用小驼峰命名(camelCase)，首字母保持小写，不使用下划线

2. 类名使用大驼峰(CamelCase)命名风格，首字母大写，私有类可用一个下划线开头

3. **函数名、变量名一律小写，如有多个单词，用下划线隔开**，私有函数用一个下划线开头

4. 常量采用全大写，如有多个单词，使用下划线隔开

5. 输出语句中使用单双引号均可，正则表达式使用双引号、文档字符串 (docstring) 推荐使用三个双引号

6. 模块导入：
   导入应该放在文件顶部，位于模块注释和文档字符串之后，模块全局变量和常量之前。
   导入应该照从最通用到最不通用的顺序分组，分组之间空一行，依次为：标准库导入 -> 第三方库导入 -> 应用程序指定导入
   每个 import 语句只导入一个模块，尽量避免一次导入多个模块

   同类型模块放一起，不同模块用一行隔开

7. 空行
   双空行：编码格式声明、模块导入、常量和全局变量声明、顶级定义（类的定义）和执行代码之间空两行
   单空行：方法定义之间空一行，方法内分隔某些功能的位置也可以空一行

8. 在文件开头声明文件编码，以下两种均可
   `\# -*- coding: utf-8 -*-  `
   `\# coding = utf-8`

9. 缩进规则
   统一使用 4 个空格进行缩进，不要用tab, 更不要tab和空格混用

10. 注释部分，# 号后面要空一格
    `\# 注释部分 `

11. 每个函数均需带有如下格式的注释，

    ```python
    def save_wav_from_url(url, spk, receive_path,save_days=30):
        """save wav file from post request.
    
        Args:
            file (request.file): wav file.
            spk (string): speack id
            receive_path (string): save path
    
        Returns:
            string: file path
        """
        
        xxxxxxx
    ```

12. 所有函数返回值利用dict包裹，而不是直接return，方便后续修改或更新。

    ```python
    def downaload_file(url):
        """save wav file from post request.
    
        Args:
            url (string): file url
        Returns:
            string: file_path
            string: message
        """
        file_path = "xxxx"
        message = "okay"
        
        return {
            "file_path":file_path,
            "message": message
        }
    ```

13. 每行不超过120个字符
14. 每个文件最末尾加一个空行
15. Python格式使用pylint工具扫描





```shell
src
 - utils
 vvs.py
 cfg.py
```





## 二、核心模块 (赵)


### 1. 注册模块（utils/register）

详见接口文档



### 2. 对比模块（utils/test）

详见接口文档



### 3. 音频预处理模块（utils/preprocess）

#### 3.1 音频读取

```
函数：
	from utils.preprocess import read_wav
入参：
	1. filepath : 文件地址（string)
	2. channel : 使用的通道编号（int）
输出：
	1. wav_data 音频数据 (1D numpy array)
	2. sr 音频采样率 (int)
```



#### 3.2 有效片段提取及静默音消除

```
函数：
	from utils.preprocess import vad
入参：
	1. wav_data : 音频数据 (1D numpy array)
	2. sr : 音频采样率 (int)
输出：
	1. wav_data 消除静音片段后的音频数据 (1D numpy array)
	2. wav_info 音频的起始和终止位置 (2D numpy array)
```



#### 3.3 音频重采样

```
函数：
	from utils.preprocess import resample
入参：
	1. wav_data : 音频数据 (1D numpy array)
	2. sr : 音频采样率 (int)
	3. dst_sr : 目标采样率 (int)
输出：
	1. wav_data 重采样后的音频数据 (1D numpy array)
```



#### 3.4 音频降噪

```
函数：
	from utils.preprocess import denoise
入参：
	1. wav_data : 音频数据 (1D numpy array)
	2. sr : 音频采样率 (int)
输出：
	1. wav_data 降噪后的音频数据 (1D numpy array)
```



#### 3.5 音频回声消除

```
函数：
	from utils.preprocess import echo
入参：
	1. wav_data : 音频数据 (1D numpy array)
	2. sr : 音频采样率 (int)
输出：
	1. wav_data 回声消除后的音频数据 (1D numpy array)
```



#### 3.6 音频削峰检测

```
函数：
	from utils.preprocess import clip
入参：
	1. wav_data : 音频数据 (1D numpy array)
	2. sr : 音频采样率 (int)
输出：
	1. clip : 是否存在削峰 (boolean)
```



#### 3.7 音频高质量片段提取

```
函数：
	from utils.preprocess import get_useful
入参：
	1. wav_data : 音频数据 (1D numpy array)
	2. sr : 音频采样率 (int)
输出：
	1. wav_data 提取的音频数据 (1D numpy array)
```



#### 3.8 多条音频拼接

```
函数：
	from utils.preprocess import concat
入参：
	1. wav_data : 多条音频数据 (2D numpy array)
	2. sr : 音频采样率 (int)
输出：
	1. wav_data 拼接的音频数据 (1D numpy array)
```



#### 3.9 音频下载

```
函数：
	from utils.preprocess import download
入参：
	1. url : 音频文件地址 (2D numpy array)
	2. dst_path : 期望保存的地址 (string)
输出：
	1. save_path 保存在本机的路径 (1D numpy array)
```



### 4. 特征提取模块(utils/encoder)

#### 4.1 特征编码

```
函数：
	from utils.preprocess import encode
入参：
	1. wav_data : 音频文件信息 (1D numpy array)
输出：
	1. feature 长度为192的特征向量 (1D numpy array)
```

#### 4.2 音频打分

```
函数：
	from utils.preprocess import score
入参：
	1. wav_data : 音频文件信息 (1D numpy array)
	1. wav_data_r : 音频文件信息 (1D numpy array)
输出：
	1. cosine 余弦相似度 (float)
```

#### 4.3 音频预分类

```
函数：
	from utils.preprocess import classify
入参：
	1. wav_data : 音频文件信息 (1D numpy array)
输出：
	1. class_num 类别 (int)
```





### 5. 分布式存储及数据库模块(utils/oss)

#### 5.1 文件上传至指定桶

```
函数：
	from utils.oss import upload
入参：
	1. file_path : 音频文件保存在本机的路径 (string)
	2. bucket : minio桶名称 (string)
	3. days : 保存的天数 (int)
输出：
	1. url : 音频文件地址 (string)
```



#### 5.2 列出指定桶的所有文件

```
函数：
	from utils.oss import list_files
入参：
	1. bucket : minio桶名称 (string)
	2. time_start :  时间范围起始值(string)
	3. time_end :  时间范围终止值(string)
	4. prefix :  前缀(string)
	5. suffix : 后缀(string)
输出：
	1. url_list : 音频文件地址列表 (list[string])
```



#### 5.3 桶信息获取

```
函数：
	from utils.oss import list_files
入参：
	1. bucket : minio桶名称 (string)
输出：
	1. file_number : 文件总数(int)
	1. fold_number : 子文件夹数(int)
```



### 6. 通用模块（utils/global）

#### 6.1 音频下载并上传至minio

```
函数：
	from utils.global import download_and_upload
入参：
	1. url : 音频文件地址 (string)
	2. dst_path : 期望保存的地址 (string)
	3. bucket : minio桶名称 (string)
输出：
	1. save_path 保存在本机的路径 (string)
	2. minio_path 保存的minio地址 (string)
	3. file_size 文件大小 (float)
	4. file_type 文件类型 (string)
```



#### 6.3 音频预处理

```
函数：
	from utils.global import preprocess
入参：
	1. file_path : 音频文件路径 (string)
	2. device : 使用的设备，cpu或者cuda (string)

输出：
	1. wav_data 预处理后的音频数据 (1D numpy array)
```



#### 6.2 音频有效性检验

```
函数：
	from utils.global import check
入参：
	1. wav_data : 音频数据 (1D numpy array)
输出：
	1. pass 是否通过检验 (boolean)
	2. error_type 错误类型 (int)
	3. error_message 错误原因 (string)
```

### 7. 手机号处理模块

#### 7.1 归属地等信息获取

## 三、自动注册服务 (薛)

### 1. 文件夹监控

通过rclone或其他同步服务，实现系统指定文件夹与minio桶的同步更新。当文件夹有新的文件写入时，将其同步上传至minio指定桶内进行存储。

181 -》 black/2022-09-02/1.wav -〉 black_bucket         grey/2022-09-02/1.wav -> grey_bucket

Url - > minio

### 2. 自动注册

import minio

通过Flask服务或shell脚本实现定时对minio指定桶进行扫描，当发现未注册或测试的新文件时，自动调用注册或对比接口。



## 四、Docker镜像 (薛)

### 1. 镜像制作

声纹识别后端以及自动注册服务的镜像制作。

### 2. 维护与更新

搭建公司内部Docker私有仓库，进行各版本维护、更新等等。

### 3. Nvidia-Docker离线安装包

下载适用于各个操作系统的Nvidia-Docker离线安装包及相关依赖，并编写安装部署及维护说明书。

### 4. GPU的CUDA+NVIDIA驱动

下载适用于不同架构NVIDIA GPU的CUDA安装包及相关驱动，并编写安装部署及维护说明书。



## 五、 测试数据的准备 (潘)

### 1. 数据选取

选择500对以上测试数据，其中正负样本比例保持约1:1。

### 2. shell脚本准备

Docker部署前后对模型进行测试，实现：

1. 音频正确注册
2. 音频正确测试
3. 不合格音频正常被检出
4. 判黑比例与预期相符

重复多次测试模型效率，可以直接返回模型运行状况及运行效率情况（CPU/GPU），便于后续开发测试。





## 六、 数据库 (潘)

### 1. MySQL

实现MySQL的离线部署，实现多服务器的集群部署、容灾备份等等，编写相关部署及维护说明书。

维护各迭代版本数据库设计的sql文件。

### 2. Redis

实现Redis的离线部署，实现多服务器的集群部署、容灾备份等等，编写相关部署及维护说明书。



## 七、分布式存储 (薛)

### 1. MinIO分布式部署

实现Minio的集群部署及分布式存储，编写相关部署及维护说明书。



## 八、第二阶段计划

1. 核心算法模块的C++重构
2. 说话人声纹定时更新功能
3. 项目整体源码保护