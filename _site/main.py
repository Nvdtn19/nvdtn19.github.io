from pyvz2rijndael import RijndaelCBC
import base64
import zlib
import binascii
import struct
import sys
import os
import hashlib


key = "65bd1b2305f46eb2806b935aab7630bb"
tool = RijndaelCBC(key=key, block_size=24)
magic = "DEADFED4"


def decode(data: bytes):
    step1 = base64.b64decode(data)[2:]
    step2 = tool.decrypt(step1)[8:]
    step3 = zlib.decompress(step2)
    return step3

def encode(data: bytes):
    step1 = binascii.unhexlify(magic) + struct.pack("<I", len(data)) + zlib.compress(data)
    step2 = tool.encrypt(step1)
    step3 = base64.b64encode(b"\x10\0" + step2)
    return step3


def process_translation(input_file, output_dir, platform):
    # Читаем входной файл
    with open(input_file, "rb") as f:
        translation = f.read()

    # Генерация pvz2_l.txt
    pvz2_content = encode(translation)
    with open(os.path.join(output_dir, "pvz2_l.txt"), "wb") as f:
        f.write(pvz2_content)

    h = hashlib.md5(translation).hexdigest()
    d = {
        "File": {
            "Name": "pvz2_l.txt",
            "Hash": str(h)
        }
    }
    # Генерация file_list.txt
    file_list_content = encode(str(d).encode())
    with open(os.path.join(output_dir, "file_list.txt"), "wb") as f:
        f.write(file_list_content)

    print(f"Processed {platform} translation: {input_file}, files saved to {output_dir}")


if __name__ == '__main__':
    raw_file = sys.argv[1]  # Путь к файлу перевода
    out_dir = sys.argv[2]  # Путь к выходной папке
    op_system = sys.argv[3]  # Платформа (ad или ios)

    os.makedirs(out_dir, exist_ok=True)
    process_translation(raw_file, out_dir, op_system)
