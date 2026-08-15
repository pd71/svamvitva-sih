import os
import zipfile
import urllib.request
import ssl

DATASET_DIR = os.path.abspath("./svamitva_dataset_repository")
DOWNLOAD_DIR = os.path.join(DATASET_DIR, "downloaded")
EXTRACT_DIR = os.path.join(DATASET_DIR, "extracted")

os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs(EXTRACT_DIR, exist_ok=True)

OFFICIAL_LINKS = {
    "Maharashtra": "https://svamitva.nic.in/DownloadPDF/TifFile/Maharashtra_1.zip",
    "Gujarat": "https://svamitva.nic.in/DownloadPDF/TifFile/Gujarat_5.zip",
    "MP": "https://svamitva.nic.in/DownloadPDF/TifFile/MP_shape.zip",
    "Chhattisgarh": "https://svamitva.nic.in/DownloadPDF/TifFile/Chhattisgarh_2.zip",
    "Gautam_Budh_Nagar": "https://svamitva.nic.in/DownloadPDF/TifFile/Gautam_budh_Nagar_2.zip"
}

def download_file(url: str, output_path: str) -> bool:
    print(f"Downloading {url} -> {output_path}...")
    # Bypass SSL verification if government cert is self-signed/expired
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    )

    try:
        with urllib.request.urlopen(req, context=ctx) as response, open(output_path, 'wb') as out_file:
            # Print total bytes
            total_size = response.getheader('Content-Length')
            if total_size:
                print(f"Total size: {int(total_size) / 1024 / 1024:.2f} MB")
            chunk_size = 1024 * 1024  # 1MB chunks
            while True:
                chunk = response.read(chunk_size)
                if not chunk:
                    break
                out_file.write(chunk)
        print(f"Successfully downloaded {output_path}")
        return True
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return False

def extract_zip(zip_path: str, target_dir: str):
    print(f"Extracting {zip_path} to {target_dir}...")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(target_dir)
        print("Extraction complete.")
    except Exception as e:
        print(f"Error extracting {zip_path}: {e}")

def run_download_pipeline():
    for name, url in OFFICIAL_LINKS.items():
        zip_filename = os.path.basename(url)
        zip_path = os.path.join(DOWNLOAD_DIR, zip_filename)
        
        if not os.path.exists(zip_path):
            success = download_file(url, zip_path)
            if not success:
                continue
        
        target_extract = os.path.join(EXTRACT_DIR, name)
        os.makedirs(target_extract, exist_ok=True)
        extract_zip(zip_path, target_extract)

if __name__ == "__main__":
    run_download_pipeline()
