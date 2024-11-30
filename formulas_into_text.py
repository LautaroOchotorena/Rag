import re
import config_api_key
from langchain_google_genai import ChatGoogleGenerativeAI

# Función para detectar segmentos LaTeX en un archivo .md
def extract_latex_segments(md_file_path):
    with open(md_file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Busca todos los segmentos LaTeX con $$...$$ o $...$
    latex_segments = re.findall(r'\$\$(.*?)\$\$|\$(.*?)\$', content, re.DOTALL)
    
    # Filtra solo los segmentos que tienen contenido (ignora las tuplas vacías)
    return [segment[0] if segment[0] else segment[1] for segment in latex_segments]

llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0.1)   
# Función para enviar el segmento a un modelo LLM para compactar
def compact_latex(latex_text):
    try:
        # Solicitar al modelo de lenguaje GPT-4 mini que compacte el LaTeX
        prompt = f"Compacta en texto plano la siguiente expresión matemática en LaTeX: {latex_text}. Sólo respondé con la compactación directa"

        # Usar el modelo para generar la respuesta
        response = llm.invoke(prompt)
        response_content = dict(response)['content']
        return response_content.replace('\n','')
    except Exception as e:
        print(f"Error al procesar LaTeX: {e}")
        return latex_text

# Función principal para procesar el archivo y compactar los segmentos
def process_md_file(md_file_path, output_file_path):
    # Extrae los segmentos LaTeX
    latex_segments = extract_latex_segments(md_file_path)
    
    # Compacta cada segmento y reemplázalo en el contenido original
    with open(md_file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    for latex in latex_segments:
        compacted = compact_latex(latex)
        content = content.replace(f"$${latex}$$", f"{compacted}").replace(f"${latex}$", f"{compacted}").replace("ï¼Œ", ",")
    
    # Guarda el nuevo contenido con los LaTeX compactados
    with open(output_file_path, 'w', encoding='utf-8') as file:
        file.write(content)

# Ruta al archivo markdown de entrada y salida
md_file_path = 'probando.md'
output_file_path = 'archivo_salida.md'

# Procesa el archivo
process_md_file(md_file_path, output_file_path)

print("Archivo procesado con éxito.")
