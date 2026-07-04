from littlefs import LittleFS

try:
    fs = LittleFS(block_size=512, block_count=30720000, mount=False)
    with open("lfs_image.bin", "rb") as fh:
        fs.context.buffer = bytearray(fh.read())
    fs.mount()
    with fs.open("config.txt", "r") as f:
        print("Verification Success! File Content:")
        print(f.read())
except Exception as e:
    print(f"Verification Failed: Filesystem corrupt or unreadable. Error: {e}")
