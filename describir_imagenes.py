import google.generativeai as genai
import config_api_key
import re

def describir(path_image, text='Ninguno'):
    # Upload the file.
    sample_file = genai.upload_file(path=path_image)

    # Choose a Gemini model.
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")

    text_template = f"Contexto de la figura: {text}. Haz una breve descripción de la figura."
    # Prompt the model with text and the previously uploaded image.
    response = model.generate_content([sample_file, text_template])

    return response.text

def process_context_with_images(context):
    # Encuentra todas las referencias de imágenes
    image_paths = re.findall(r'!\[\]\((.+?)\)', context)
    
    for image_path in image_paths:
        # Interpreta la imagen y genera una descripción en texto
        image_path_correcto = "./md/merged_files/" + image_path.replace("./","")

        image_text = describir(image_path_correcto, context)
        # Reemplaza la referencia de la imagen en el contexto
        context = context.replace(f"![]({image_path})", image_text)
    
    return context

if __name__ == "__main__":
    import time
    # Se le tiene que pasar el image_path como estaría en el md
    image_path = "./images/f0cAlK6FrIZx03uPmCBzmIg0qF5rVDAMv.png"
    image_path_correcto = "./md/merged_files/" + image_path.replace("./","")
    inicio = time.time()
    print(describir(image_path_correcto))
    fin = time.time()
    print(f"Tiempo de ejecución: {round(fin - inicio, 2)} segundos")