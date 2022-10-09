RECIPE

目标格式：
```shell
├── data
│   └── dataset_name (数据集名称)
│       ├── 13160050611 (每个说话人一个目录，目录名为说话人ID)
│       │   ├── 1.wav   (每个文件一个编号，从1开始)
│       │   └── 2.wav
│       └── 15151832002
│           ├── 1.wav
│           ├── 2.wav
│           └── 3.wav
└── dataset_name.csv (数据集信息)
```
dataset_name：
1. cjsd(长江时代语音数据集)
2. aishell(aishell1语音数据集)
3. ctcc(电信数据)

　csv 文件记录每条音频的以下信息：
1. speaker_id 说话人ID
2. wav_number WAV编号
3. file_size 文件大小（字节数）
4. speech_duration（毫秒）
5. gender（性别 F/M）
6. channel(有效音频所在通道数)