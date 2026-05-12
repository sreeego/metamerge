# 🖼️ MetaMerge

A lightweight Python utility to restore metadata from Google Photos Takeout sidecar files back into your images and videos.

---

## 🚀 Overview

MetaMerge rebuilds missing EXIF and media metadata from Google Photos Takeout exports. When exporting media using Google Takeout, important metadata such as timestamps, GPS coordinates, and camera information are often stored separately inside `.json` sidecar files instead of being embedded directly into the actual files.

MetaMerge automatically detects these sidecar files, extracts the metadata, and embeds it back into the corresponding images and videos while preserving the original folder structure.

---

## ✨ Features

### 🧩 Automatic Metadata Restoration

* Detects Google Photos Takeout sidecar files automatically
* Restores EXIF metadata directly into images

### 🍎 HEIC / HEIF Support

* Supports HEIC and HEIF images from iPhones
* Preserves metadata during processing

### 🎥 Video Metadata Support

* Restores metadata for video files
* Supports:

  * `.mp4`
  * `.mov`
  * `.mkv`
  * `.avi`
  * `.3gp`
  * `.wmv`
* Restores creation date and GPS metadata where available

### 📂 Recursive Folder Processing

* Scans nested folders recursively
* Preserves original directory structure

### 🛡️ Non-Destructive Workflow

* Original files remain untouched
* Processed files are written to a separate output directory

### ⚡ Lightweight & Fast

* Minimal dependencies
* Efficient batch processing
* Simple command-line workflow

### 📋 Smart File Handling

* Copies files without sidecars safely
* Handles broken or unsupported metadata gracefully

---

## 📑 Supported Formats

| Format      | Extension        | Metadata Supported            |
| ----------- | ---------------- | ----------------------------- |
| JPEG        | `.jpg`, `.jpeg`  | EXIF (date, GPS, camera info) |
| PNG         | `.png`           | EXIF (date, GPS)              |
| WEBP        | `.webp`          | EXIF (date, GPS)              |
| HEIC / HEIF | `.heic`, `.heif` | EXIF (date, GPS, camera info) |
| TIFF        | `.tiff`          | EXIF (date, GPS)              |
| BMP         | `.bmp`           | EXIF (date, GPS)              |
| GIF         | `.gif`           | EXIF (date, GPS)              |
| MP4         | `.mp4`           | Date, GPS                     |
| MOV         | `.mov`           | Date, GPS                     |
| MKV         | `.mkv`           | Date                          |
| AVI         | `.avi`           | Date                          |
| WMV         | `.wmv`           | Date                          |
| 3GP         | `.3gp`           | Date, GPS                     |

---

## ⚠️ Requirements

### FFmpeg

FFmpeg is required for video metadata processing.

Download: https://ffmpeg.org/download.html

Make sure `ffmpeg` is added to your system PATH.

### HEIC / HEIF Support

Install `pillow-heif` for HEIC/HEIF image support:

```bash id="d5xgva"
pip install pillow-heif
```

---

## ⚙️ Usage

### Basic Command

```bash id="grk2fi"
python metamerge.py --input <takeout-folder> --output <output-folder>
```

### Example

```bash id="s9qvxf"
python metamerge.py ^
  --input "D:\Takeout\Google Photos" ^
  --output "D:\MergedPhotos"
```

---

## 🧾 Command Line Arguments

| Argument   | Short | Description                             |
| ---------- | ----- | --------------------------------------- |
| `--input`  | `-i`  | Path to Google Photos Takeout folder    |
| `--output` | `-o`  | Destination folder for processed images |

---

## 📦 Installation

### 1. Clone Repository

```bash id="r0ywrn"
git clone https://github.com/sreeego/metamerge.git

cd metamerge
```

### 2. Install Dependencies

```bash id="ffkqmk"
pip install -r requirements.txt
```

### 3. requirements.txt

```txt id="l0x6rj"
Pillow>=10.0.0
piexif>=1.1.3
pillow-heif>=0.16.0
```

### 4. Run MetaMerge

```bash id="cjlwm7"
python metamerge.py --input "<takeout-folder>" --output "<output-folder>"
```

---

## 📂 Project Structure

```text id="ehgqk7"
metamerge/
├── .gitignore
├── LICENSE
├── metamerge.py
├── README.md
└── requirements.txt
```

---

## 🔄 How It Works

1. Scans the input directory recursively

2. Finds supported image and video files

3. Searches for matching `.json` sidecar files

4. Extracts metadata from the sidecar

5. Embeds metadata into the media file

6. Saves processed files to the output directory

---

## 📄 Example Output

```text id="r2w6eh"
✅ IMG_1024.jpg

✅ IMG_1025.heic

✅ VID_2048.mp4

⚠️ IMG_1026.jpg → copied, no sidecar

❌ IMG_1027.jpg → invalid metadata

Done!

Merged:     3

No sidecar: 1

Errors:     1

Output:     D:\MergedPhotos
```

---

## 📸 Use Cases

* Restore original timestamps after Google Takeout export

* Preserve chronological ordering in gallery applications

* Rebuild EXIF metadata for photo management software

* Archive Google Photos libraries with embedded metadata

---

## 🏗️ Tech Stack

* **Language:** Python

* **Image Processing:** Pillow, pillow-heif

* **EXIF Handling:** piexif

* **Video Metadata:** FFmpeg

---

## 📜 License

MIT License © 2026 SREE GOVIND S A

---

## 👤 Author

* GitHub: [sreeego](https://github.com/sreeego)
