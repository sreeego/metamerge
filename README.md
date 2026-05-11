# 🖼️ MetaMerge

A lightweight Python utility to restore metadata from Google Photos Takeout sidecar files back into your images.

---

## 🚀 Overview

MetaMerge rebuilds missing EXIF metadata from Google Photos Takeout exports. When exporting photos using Google Takeout, important metadata such as timestamps, GPS coordinates, and image details are often stored separately inside `.json` sidecar files instead of being embedded directly into the photos.

MetaMerge automatically detects these sidecar files, extracts the metadata, and embeds it back into the corresponding images while preserving the original folder structure.

---

## ✨ Features

### 🧩 Automatic Metadata Restoration

* Detects Google Photos Takeout sidecar files automatically
* Restores EXIF metadata directly into images

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

## ⚙️ Usage

### Basic Command

```bash id="z6wj5o"
python metamerge.py --input <takeout-folder> --output <output-folder>
```

### Example

```bash id="qob1o2"
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

```bash id="3xf6j1"
git clone https://github.com/sreeego/metamerge.git

cd metamerge
```

### 2. Install Dependencies

```bash id="nvv1rm"
pip install -r requirements.txt
```

### 3. Run MetaMerge

```bash id="tb3sow"
python metamerge.py --input "<takeout-folder>" --output "<output-folder>"
```

---

## 📂 Project Structure

```text id="sm3umk"
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

2. Finds supported image files

3. Searches for matching `.json` sidecar files

4. Extracts metadata from the sidecar

5. Embeds metadata into the image using EXIF

6. Saves processed images to the output directory

---

## 📄 Example Output

```text id="c7q2vk"
✅ IMG_1024.jpg

✅ IMG_1025.jpg

⚠️ IMG_1026.jpg → copied, no sidecar

❌ IMG_1027.jpg → invalid metadata

Done!

Merged:     2

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

* **Image Processing:** Pillow

* **EXIF Handling:** piexif

---

## 📜 License

MIT License © 2026 SREE GOVIND S A

---

## 👤 Author

* GitHub: [sreeego](https://github.com/sreeego)
