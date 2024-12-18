import google.generativeai as genai
import config_api_key
import re
import time

def describe(path_image, text='None'):
    # Upload the file
    sample_file = genai.upload_file(path=path_image)

    # Gemini model
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")

    text_template = f"Figure context: {text}. Provide a brief description of the figure"
    # Prompt the model with text and the previously uploaded image.
    response = model.generate_content([sample_file, text_template])

    return response.text

def process_context_with_images(context):
    # Find all image references
    image_paths = re.findall(r'!\[\]\((.+?)\)', context)
    
    for image_path in image_paths:
        correct_image_path = "./md/merged_files/" + image_path.replace("./","")

        image_text = describe(correct_image_path, context)
        # Replace the image reference to a description of the image
        context = context.replace(f"![]({image_path})", image_text)
    
    return context

if __name__ == "__main__":
    # The image_path must be passed as it would be in the md folder
    image_path = "./images/fVN4MaqpD4VgIaHoaq6SvUh9KFCLgirRk.png"
    image_path_correcto = "./md/merged_files/" + image_path.replace("./","")
    start = time.time()
    print(describe(image_path_correcto))
    end = time.time()
    print(f"Execution time: {round(end - start, 2)} seconds")