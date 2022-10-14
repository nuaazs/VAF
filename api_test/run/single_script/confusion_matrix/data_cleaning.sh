rm -rf 2.sh
rm -rf /mnt/panjiawei/run_2/data/new/json.json
rm -rf /mnt/panjiawei/run_2/data/new/noblack.txt
rm -rf /mnt/panjiawei/run_2/data/new/zhuanban.txt
python3 cjsd_data.py > 2.sh
rm -rf /mnt/panjiawei/run_2/data/black/*
rm -rf /mnt/panjiawei/run_2/data/gray/*
sudo rm -rf /var/lib/docker/volumes/c0a98b5ece2cbd3d5f8f7346bce6bcb561cadfeecb9e27bcb41d6873b76bb464/_data/gray/*
sudo rm -rf /var/lib/docker/volumes/c0a98b5ece2cbd3d5f8f7346bce6bcb561cadfeecb9e27bcb41d6873b76bb464/_data/black/*
sudo rm -rf /var/lib/docker/volumes/c0a98b5ece2cbd3d5f8f7346bce6bcb561cadfeecb9e27bcb41d6873b76bb464/_data/raw/*
sudo rm -rf /var/lib/docker/volumes/c0a98b5ece2cbd3d5f8f7346bce6bcb561cadfeecb9e27bcb41d6873b76bb464/_data/preprocessed/*
bash 2.sh
python3 ../test/download.py
rm -rf /mnt/panjiawei/run_2/plog/*