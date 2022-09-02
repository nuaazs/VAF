# @Time    : 2022-07-27  18:57:38
# @Author  : zhaosheng
# @email   : zhaosheng@nuaa.edu.cn
# @Blog    : http://www.iint.icu/
# @File    : /mnt/zhaosheng/VAF-System/src/utils/oss.py
# @Describe: Minio sdk for python.

from minio import Minio
from datetime import timedelta
import cfg
from minio import Minio
from minio.commonconfig import GOVERNANCE
from minio.retention import Retention
from datetime import datetime

HOST = f"{cfg.MINIO['host']}:{cfg.MINIO['port']}"

ACCESS_KEY = cfg.MINIO['access_key']
SECRET_KEY = cfg.MINIO['secret_key']
client = Minio(
        HOST,
        access_key=ACCESS_KEY,
        secret_key=SECRET_KEY,
        secure=False
    )

found = client.bucket_exists("raw")
if not found:
    client.make_bucket(bucket_name="raw",object_lock=True)
else:
    print("Bucket 'raw' already exists")

found = client.bucket_exists("preprocessed")
if not found:
    client.make_bucket(bucket_name="preprocessed",object_lock=True)
else:
    print("Bucket 'preprocessed' already exists")

    
def upload_file(bucket_name='raw',filepath="/VAF-System/demo_flask/utils/orm.py",filename='orm.py',save_days=30):
    # Upload data with tags, retention and legal-hold.
    date = datetime.utcnow().replace(
        hour=0, minute=0, second=0, microsecond=0,
    ) + timedelta(days=save_days)

    if save_days < 0:
        result = client.fput_object(
            bucket_name, filename, filepath,
            legal_hold=True,
        )
    else:
        result = client.fput_object(
            bucket_name, filename, filepath,
            retention=Retention(GOVERNANCE, date),
            legal_hold=True,
        )
    print(
        "created {0} object; etag: {1}, version-id: {2}".format(
            result.object_name, result.etag, result.version_id,
        ),
    )

    return f"http://{HOST}/{bucket_name}/{filename}"