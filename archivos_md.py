import os
import re
import shutil

# Ruta de la carpeta principal
main_folder = "./md/"

# Crear una carpeta de destino para los archivos combinados
output_folder = os.path.join(main_folder, "merged_files")
os.makedirs(output_folder, exist_ok=True)

# Buscar archivos .md y agrupar por prefijo común
md_files = {}
for root, dirs, files in os.walk(main_folder):
    for file in files:
        if file.endswith(".md"):
            # Obtener el prefijo del archivo
            prefix = re.sub(r'_part\d+\.md$', '', file)
            prefix = prefix.replace(".md", "")
            md_files.setdefault(prefix, []).append(os.path.join(root, file))

# Procesar grupos de archivos .md con el mismo prefijo
for prefix, files in md_files.items():
    if len(files) > 0:
        # Combinar el contenido de los archivos .md en un nuevo archivo
        combined_md_path = os.path.join(output_folder, f"{prefix}.md")
        with open(combined_md_path, 'w', encoding='utf-8') as combined_md:
            for md_file in files:
                with open(md_file, 'r', encoding='utf-8') as f:
                    combined_md.write(f.read())
                    combined_md.write("\n\n")  # Separador entre contenidos
                
        # Copiar las carpetas de imágenes correspondientes
        combined_images_folder = os.path.join(output_folder, "images")
        os.makedirs(combined_images_folder, exist_ok=True)
        
        for md_file in files:
            images_folder = os.path.join(os.path.dirname(md_file), "images")
            if os.path.exists(images_folder):
                for image in os.listdir(images_folder):
                    src_image_path = os.path.join(images_folder, image)
                    dest_image_path = os.path.join(combined_images_folder, image)
                    # Evitar duplicados en caso de imágenes con el mismo nombre
                    if not os.path.exists(dest_image_path):
                        shutil.copy2(src_image_path, dest_image_path)

print("Unión de archivos completada.")