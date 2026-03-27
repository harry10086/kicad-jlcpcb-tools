import os
import sys
import shutil
import zipfile
import re

def build_plugin(version):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    pcm_dir = os.path.join(base_dir, "PCM")
    archive_dir = os.path.join(pcm_dir, "archive")
    
    # Clean up old files
    print("Clean up old files")
    for f in os.listdir(pcm_dir):
        if f.endswith(".zip"):
            os.remove(os.path.join(pcm_dir, f))
    if os.path.exists(archive_dir):
        shutil.rmtree(archive_dir)
        
    # Create folder structure
    print("Create folder structure for ZIP")
    plugins_dir = os.path.join(archive_dir, "plugins")
    resources_dir = os.path.join(archive_dir, "resources")
    os.makedirs(plugins_dir)
    os.makedirs(resources_dir)
    
    # Copy files
    print("Copy files to destination")
    if os.path.exists(os.path.join(base_dir, "VERSION")):
        shutil.copy(os.path.join(base_dir, "VERSION"), plugins_dir)
    
    for f in os.listdir(base_dir):
        if f.endswith(".py") or f.endswith(".png"):
            shutil.copy(os.path.join(base_dir, f), plugins_dir)
            
    if os.path.exists(os.path.join(base_dir, "settings.json")):
        shutil.copy(os.path.join(base_dir, "settings.json"), plugins_dir)
        
    shutil.copytree(os.path.join(base_dir, "icons"), os.path.join(plugins_dir, "icons"))
    shutil.copytree(os.path.join(base_dir, "lib"), os.path.join(plugins_dir, "lib"))
    
    os.makedirs(os.path.join(plugins_dir, "core"))
    for f in os.listdir(os.path.join(base_dir, "core")):
        if f.endswith(".py"):
            shutil.copy(os.path.join(base_dir, "core", f), os.path.join(plugins_dir, "core"))
            
    shutil.copy(os.path.join(pcm_dir, "icon.png"), resources_dir)
    shutil.copy(os.path.join(pcm_dir, "metadata.template.json"), os.path.join(archive_dir, "metadata.json"))
    
    print("Write version info to file")
    with open(os.path.join(plugins_dir, "VERSION"), "w", encoding="utf-8") as f:
        f.write(version)
        
    print("Modify archive metadata.json")
    metadata_path = os.path.join(archive_dir, "metadata.json")
    with open(metadata_path, "r", encoding="utf-8") as f:
        meta_data = f.read()
        
    meta_data = meta_data.replace("VERSION_HERE", version)
    meta_data = meta_data.replace('"kicad_version": "6.0",', '"kicad_version": "6.0"')
    
    lines = meta_data.split("\n")
    lines = [line for line in lines if "SHA256_HERE" not in line and "DOWNLOAD_SIZE_HERE" not in line and "DOWNLOAD_URL_HERE" not in line and "INSTALL_SIZE_HERE" not in line]
    meta_data = "\n".join(lines)
    
    with open(metadata_path, "w", encoding="utf-8") as f:
        f.write(meta_data)
        
    print("Zip PCM archive")
    zip_name = os.path.join(pcm_dir, f"KiCAD-PCM-{version}.zip")
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, set_files in os.walk(archive_dir):
            for file in set_files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, archive_dir)
                zipf.write(file_path, arcname)
                
    print(f"Successfully created: {zip_name}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python build.py <version>")
        sys.exit(1)
    build_plugin(sys.argv[1])
