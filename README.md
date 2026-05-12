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

| Format      | Extension        | Metadata Supported                 |
| ----------- | ---------------- | ---------------------------------- |
| JPEG        | `.jpg`, `.jpeg`  | Date, GPS, camera info             |
| PNG         | `.png`           | Date, GPS                          |
| WEBP        | `.webp`          | Date, GPS                          |
| HEIC / HEIF | `.heic`, `.heif` | Date, GPS, camera info             |
| TIFF        | `.tiff`          | Date, GPS                          |
| BMP         | `.bmp`           | Date, GPS                          |
| GIF         | `.gif`           | Date, GPS                          |
| MP4         | `.mp4`           | Date, GPS                          |
| MOV         | `.mov`           | Date, GPS                          |
| 3GP         | `.3gp`           | Date, GPS                          |
| MKV         | `.mkv`           | Date only *(container limitation)* |
| AVI         | `.avi`           | Date only *(container limitation)* |
| WMV         | `.wmv`           | Date only *(container limitation)* |

---

## ⚠️ Requirements

### FFmpeg

FFmpeg is required for video metadata processing.

Download: https://ffmpeg.org/download.html

Make sure `ffmpeg` is added to your system PATH.

### HEIC / HEIF Support

Install `pillow-heif` for HEIC/HEIF image support:

```bash id="vlcq7x"
pip install pillow-heif
```

---

## ⚙️ Usage

### Basic Command

```bash id="yq6lxf"
python metamerge.py --input <takeout-folder> --output <output-folder>
```

### Example

```bash id="2r2hpx"
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

```bash id="hjlwm8"
git clone https://github.com/sreeego/metamerge.git

cd metamerge
```

### 2. Install Dependencies

```bash id="cv7dqb"
pip install -r requirements.txt
```

### 3. requirements.txt

```txt id="0w0x0r"
Pillow>=10.0.0
piexif>=1.1.3
pillow-heif>=0.16.0
```

### 4. Run MetaMerge

```bash id="p1q5di"
python metamerge.py --input "<takeout-folder>" --output "<output-folder>"
```

---

## 📂 Project Structure

```text id="tvwpk9"
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

```text id="q5p7yh"
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

This project is licensed under the GNU General Public License v3.0 (GPL-3.0).

See the [LICENSE](LICENSE) file for details.

---

## 👤 Author

* GitHub: [sreeego](https://github.com/sreeego)
