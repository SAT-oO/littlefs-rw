# littlefs-rw
LittleFS configuration and RW from MacOS ARM64. 

*Instructions for how to configure disks with littleFS on macOS devices is outlined in [`LFS_CONFIGURE.md`](LFS_CONFIGURE.md). To read a configured stick, see [Read LittleFS from USB](#read-littlefs-from-usb) below.*

## MacFUSE Installation and `littlefs-fuse` Driver Compilation Guide 

0. Clone this repo

```bash
git clone --recursive https://github.com/SAT-oO/littlefs-rw.git
cd littlefs-rw
```

If you already cloned without `--recursive`, initialize the submodule:

```bash
git submodule update --init --recursive
```

1. Download a **stable release** of [macFUSE](https://macfuse.github.io). Before you do so, make sure you are aware of the following:
- The installation process requires a shutdown to enable system extensions. You should be able to see the macFUSE item in System Settings. 
- To enable system extensions, follow [this guide](https://medium.com/@connie111111/how-i-enable-system-extensions-on-apple-silicon-macs-1726a6076dc9) to avoid restarting your computer repetitively. ***If you are still unsure in what you're doing after reading the above guide, ask someone else to do this for you.***

2. Compile the `littlefs-fuse` driver

The driver lives in `littlefs-fuse-macos/` (a git submodule). It is **NOT** the official `littlefs-fuse` due to its limited support exclusive to Linux and FreeBSD. This is my personal fork with added support for macOS.

```bash
cd littlefs-fuse-macos

# Build the binary targeting Apple Silicon architectures via host LLVM
make
```

You should see a `lfs` binary at `littlefs-fuse-macos/lfs`.


--- 

## Read LittleFS from USB

Complete [LFS_CONFIGURE.md](LFS_CONFIGURE.md) first, or use an already-formatted LittleFS stick. No `block_size` or `block_count` flags are needed here—the driver reads them from the stick.

3. Raw device identification 
```bash 
diskutil list
```
Locate the target path entry (`/dev/diskX`). 

4. Unmount, then mount

Unmount any macOS volume on the stick so the raw device is free. Change `/dev/diskX` to your disk index.

```bash
diskutil unmountDisk /dev/diskX
```

In the **same folder** (`littlefs-fuse-macos/`), start the FUSE driver. Leave this terminal open while you read files.

```bash 
mkdir -p ../littlefs-mount

# Spin up the user-space filesystem driver mapping loop
sudo ./lfs -o allow_other,defer_permissions /dev/diskX ../littlefs-mount
```

In a **second terminal** (from the project root), read files from the mount point:

```bash
ls littlefs-mount
cat littlefs-mount/config.txt
```

5. Graceful dismount 
Safely tear down the active runtime driver and flush all operations in the `lfs` daemon. Stop the `lfs` process in the first terminal with `Ctrl+C` if it is still running, then:

```bash 
umount ../littlefs-mount
diskutil eject /dev/diskX
``` 

