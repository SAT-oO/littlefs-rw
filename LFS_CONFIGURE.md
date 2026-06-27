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

### Instructions 

1. Create project folder and Python `venv`. Install `littlefs-python`. 
```bash
#[in project root]
python3 -m venv venv
source venv/bin/activate
pip install littlefs-python
```

2. Stage the data source 
Since macOS cannot natively open a LittleFS drive with Finder, all files must be prepared beforehand. 
```bash
mkdir source_dir
echo "System Init OK" > source_dir/config.txt
```
This local directory acts as a staging area. Everything inside here will be frozen into the final binary image. 

3. Compile the LittleFS binary image
This command create a raw byte container `lfs-image.bin`. 
```bash 
littlefs-python create source_dir lfs_image.bin --fs-size=16mb --block-size=4096
``` 
`--fs-size` sets the exact noundary of the filesystem.
`--block-size` defines the logical erasable sectors. 

The tool parses the `source_dir`, creates the specialized inline characters, generated the metadata pairs (that track file modifications), and structures the data to how LittleFS expects to look on an actual flash chip. 

4. Identify the target media block 
```bash 
diskutil list
``` 
Identify the USB drive in the macOS device tree (eg. `disk2`, `disk7`, etc.). 

5. Unmount system volume locks 
When a USB is inserted, macOS kernel automatically attempts to probe it and lock it to prevent concurrent RW errors from other applications. The command below forces a release on the software lock, leaving raw blocks open for low-level writing. 
```bash 
diskutil unmountDisk /dev/diskX
``` 
Replace the `X` above with the actual disk index. 

6. Execute the sector-by-sector write 
```bash 
sudo dd if=lfs_image.bin of=/dev/rdiskX bs=4096 status=progress
``` 

`dd` (data duplicator) at lowest prio level of the OS:
- `if=lfs_image.bin` specifies input file 
- `of=/dev/rdiskX` speciifes output file. `rdisk` invokes the **raw character device** interface on macOS. *This completely bypasses the kernel's internal buffer cache, piping the data directly from the Python binary to the USB stick.*
- `bs=4096` specifies matching block size to the FS configuration in step 3.

