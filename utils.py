from typing import Tuple
import zlib
import glob
import os
import io

from typing import List

FILENAME_MAX_BYTES = 1
FILESIZE_MAX_BYTES = 10


def encode_files(path: str = "./assets/72x72/*.png", dest: str = "./compressed_pngs.dat"):
    data_encoded = bytes()
    files = glob.glob(path)
    for idx, emoji_png_path in enumerate(files, start=1):
        print("Processing {} - {}/{}".format(emoji_png_path, idx, len(files)))
        with open(emoji_png_path, "rb") as file:
            filename = os.path.basename(emoji_png_path).replace(".png", "")
            filesize = os.path.getsize(emoji_png_path)

            filename_byte_size = len(filename.encode("utf-8")).to_bytes(FILENAME_MAX_BYTES, byteorder="big")
            filesize_byte_size = filesize.to_bytes(FILESIZE_MAX_BYTES, byteorder="big")

            data_encoded += filename_byte_size
            data_encoded += filename.encode("utf-8")
            data_encoded += filesize_byte_size
            data_encoded += file.read()

    with open(dest, "wb") as file:
        data_encoded = zlib.compress(data_encoded, zlib.Z_BEST_COMPRESSION)
        file.write(data_encoded)


def decode_compressed_file(path: str = "./compressed_pngs.dat") -> List[Tuple[str, io.BytesIO]]:
    files = []
    with open(path, "rb") as file:
        decompressed_file = io.BytesIO(zlib.decompress(file.read()))
        while True:
            buf = decompressed_file.read(FILENAME_MAX_BYTES)
            if not buf:
                break
            filename_byte_size = int.from_bytes(buf, byteorder="big")
            filename = decompressed_file.read(filename_byte_size).decode("utf-8")
            filesize_byte_size = int.from_bytes(decompressed_file.read(FILESIZE_MAX_BYTES), byteorder="big")
            file_data = decompressed_file.read(filesize_byte_size)
            file_bytes = io.BytesIO()
            file_bytes.write(file_data)
            files.append((filename, file_bytes))

        decompressed_file.close()
    return files


if __name__ == "__main__":
    encode_files()
