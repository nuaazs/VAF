# 运行前请确认和路径是否正确

echo "删除数据"
bash clear_data.sh
echo "开始准备数据"
python3 data_preparation.py > 1.sh
echo "开始拷贝数据"
bash 1.sh
echo "开始上传数据"
python3 update_file.py
echo "开始运行数据"
# python3 confusion_matrix.py