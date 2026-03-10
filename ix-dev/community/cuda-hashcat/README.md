# CUDA Hashcat + John Ripper

GPU accelerated password cracking.

## Features
- Hashcat 7.1.2 + RTX/CUDA
- John Jumbo 1.9.0
- SSH access (cracker/password123)

## Usage
```bash
ssh cracker@node-ip -p22222
hashcat -m 0 hash.txt dict.txt
john --format=raw-md5 hash.txt