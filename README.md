# littlefs-rw
LittleFS configuration and RW from MacOS ARM64. 

*Instructions for how to configure disks with littleFS on macOS devices is outlined in [`LFS_CONFIGURE.md`](LFS_CONFIGURE.md).*

## How to read littleFS on Mac (with MacFUSE)

1. Download a **stable release** of [macFUSE](https://macfuse.github.io). The installation process requires a shutdown to enable system extensions. You should be able to see the macFUSE item in System Settings. 

2. Compile the `littlefs-fuse` driver 
The repo below is **NOT** the official `littlefs-fuse` due to its limited support exclusive to Linux and FreeBSD. 
```bash 
git clone --recursive https://github.com/jserv/littlefs-fuse.git
cd littlefs-fuse

# Build the binary targeting Apple Silicon architectures via host LLVM
make
```

3. Raw device identification 
```bash 
diskutil list
```
Locate the target path entry (`/dev/diskX`). 

4. Mount point instantiaion and I/O binding 
```bash 
mkdir -p ~/Desktop/littlefs_mount # NOTE: this is an example file path

# Spin up the user-space filesystem driver mapping loop
./lfs /dev/diskX ~/Desktop/littlefs_mount
```
**NOTE:** Alter the file path and disk index. 

5. Graceful dismount 
Safely tear down the active runtime driver and flush all operations in the `lfs` daemon.
```bash 
umount ~/Desktop/littlefs_mount
``` 

