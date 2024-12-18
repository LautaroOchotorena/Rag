import os
import re
import shutil

################################################################
# Combine the markdown parts into a single markdown file
# and place all the images in the same folder
################################################################

main_folder = "./md/"

# Create a destination folder for the combined files
output_folder = os.path.join(main_folder, "merged_files")
os.makedirs(output_folder, exist_ok=True)

# Search for .md files and group them by a common prefix
md_files = {}
for root, dirs, files in os.walk(main_folder):
    for file in files:
        if file.endswith(".md"):
            # Obtain the prefix of the file
            prefix = re.sub(r'_part\d+\.md$', '', file)
            prefix = prefix.replace(".md", "")
            md_files.setdefault(prefix, []).append(os.path.join(root, file))

# Process groups of .md files with the same prefix
for prefix, files in md_files.items():
    if len(files) > 0:
        # Combine the content of the .md files into a new file
        combined_md_path = os.path.join(output_folder, f"{prefix}.md")
        with open(combined_md_path, 'w', encoding='utf-8') as combined_md:
            for md_file in files:
                with open(md_file, 'r', encoding='utf-8') as f:
                    combined_md.write(f.read())
                    combined_md.write("\n\n")  # Separator between parts
                
        # Combine the images folders into a single folder
        combined_images_folder = os.path.join(output_folder, "images")
        os.makedirs(combined_images_folder, exist_ok=True)
        for md_file in files:
            images_folder = os.path.join(os.path.dirname(md_file), "images")
            if os.path.exists(images_folder):
                for image in os.listdir(images_folder):
                    src_image_path = os.path.join(images_folder, image)
                    dest_image_path = os.path.join(combined_images_folder, image)
                    # Avoid duplicates in case of images with the same name
                    if not os.path.exists(dest_image_path):
                        shutil.copy2(src_image_path, dest_image_path)

print("File merging completed")