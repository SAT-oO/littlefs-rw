## Configure LittleFS with MacOS

### System Architecture

```
[ Files / Directories ]  <-- Input data
          │
          ▼
   [ littlefs-python ]   <-- User-space translation tool (Builds metadata structures)
          │
          ▼
   [ lfs_image.bin ]     <-- Monolithic raw binary image of the filesystem
          │
          ▼
        [ dd ]           <-- Low-level Unix copy utility
          │
          ▼
     [ /dev/rdiskX ]     <-- Direct raw storage block access
          │
          ▼
    [ USB Storage ]      <-- Physical hardware target
```

### Instructions for Configuring USB with LFS

Follow steps 1–2, then 5–10 to stage files, build an image, and flash it to the stick. Steps 3–4 are optional and only apply if you want an empty formatted stick with no pre-staged files. After step 10, read the stick using [README](README.md#read-littlefs-from-usb).

1. Install MacFUSE and compile the `lfs` binary. See [README](README.md#macfuse-installation-and-littlefs-fuse-driver-compilation-guide) for details.
2. Identify and unmount USB

Run the following command to identify the disk index. 

```bash
diskutil list 
```

Then unmount the USB. Replace the `X` with the correct index. 

```bash
diskutil unmountDisk /dev/diskX 
```

3. Format the entire stick *(optional — skip if following steps 5–10)*

This also erases all data on the stick. 

```bash
cd littlefs-fuse-macos
sudo ./lfs --format /dev/diskX
```

4. Record the stick geometry

If you completed step 3, verify with:

```bash
sudo ./lfs --stat /dev/diskX
```

If you skipped step 3, read geometry from diskutil instead:

```bash
diskutil info /dev/diskX
```

Use `Device Block Size` as `block_size` and the `512-Byte-Units` count as `block_count`.

For a 16GB stick, `lfs --stat` after formatting should output something similar to the following: 

```bash
disk_version: lfs2.1
block_size: 512
block_count: 30720000
  used: 2/30720000 (0.0%)
  free: 30719998/30720000 (100.0%)
name_max: 255
file_max: 2147483647
attr_max: 1022
```

**Attention:** take note of the `block_size` and `block_count`. Use the same values in steps 7 and 8.

*If you only completed steps 3–4, configuration is finished—you may eject the stick. To write files to the stick, continue with step 5.* 

5. Stage files

In the project root folder, make a folder as staging buffer. Everything inside here will be frozen into the final binary image. Example shown below:

```bash
mkdir -p source_dir
echo "System Init OK" > source_dir/config.txt
```

6. Setup Python `venv`

Create project folder and Python `venv`. Install `littlefs-python`. 

```bash
#[in project root]
python3 -m venv venv
source venv/bin/activate
pip install littlefs-python
```

7. Build the LittleFS binary image

This command creates a raw byte container `lfs_image.bin`. **Make sure `block_size` and `--fs-size` match the values from step 4.**

```bash
# for a small test image (first 16MB of the stick, block_count=32768):
littlefs-python create source_dir lfs_image.bin --fs-size=16mb --block-size=512

# for the full stick image — replace with your block_size * block_count from step 4
littlefs-python create source_dir lfs_image.bin --fs-size=15728640000 --block-size=512
```

`--fs-size` equals `block_size * block_count` from step 4, and sets the exact boundary of the filesystem. 

If you're curious: The tool parses the `source_dir`, creates the specialized inline characters, generated the metadata pairs (that track file modifications), and structures the data to how LittleFS expects to look on an actual flash chip. 

8. Adjust the parameters(`block_size` and `block_count`) in [verify_config.py](verify_config.py) and run it to verify the **local** binary. Example shown below:

```bash
(venv) user@device littlefs-rw % littlefs-python create source_dir lfs_image.bin --fs-size=15728640000 --block-size=512
(venv) user@device littlefs-rw % python3 verify_config.py
Verification Success! File Content:
System Init OK
```

*So far nothing is written onto the stick yet.* 

9. Unmount the stick

```bash
diskutil unmountDisk /dev/diskX
```

10. `dd` (data duplicate) the binary to stick

`--format` before `dd` is actually redundant since `dd` overwrites the start of the stick. *Skip* `lfs --format` *if you already built* `lfs_image.bin`*—*`dd` *writes the filesystem for you.*  

**Cautious: Using** `dd` **on the wrong disk is destructive.**

```bash
sudo dd if=lfs_image.bin of=/dev/rdiskX bs=512 status=progress
```

Use the same value for `bs` as your `block_size` from step 4. Note that this process could be very slow (as in up to more than an hour long).

11. Read the stick

Follow [README](README.md#read-littlefs-from-usb) to mount the stick and confirm your files (e.g. `config.txt`).

