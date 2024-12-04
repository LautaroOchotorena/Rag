import re
import config_api_key
from langchain_google_genai import ChatGoogleGenerativeAI
import ast

# Función para detectar segmentos LaTeX en un archivo .md
def extract_latex_segments(md_file_path):
    with open(md_file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Se trató de hacer con un findall $...$ pero trae errores al considerar por ejemplo
    # "$5000" y "\$200".
    first_segment = content.split('$')
    # Filtra solo los segmentos que tienen contenido "\" que indica los segmentos de latex
    return [segment for segment in first_segment if "\\" in segment]

def extract_table_segments(md_file_path):
    with open(md_file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    table_segments = re.findall(r'<table.*?>.*?</table>', content, re.DOTALL)
    
    # Filtra solo los segmentos que tienen contenido (ignora las tuplas vacías)
    return [segment for segment in table_segments if segment.strip()]

llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0.1)   

# Función para enviar el segmento a un modelo LLM para compactar
def compact_latex(latex_text):
    try:
        # Solicitar al modelo de lenguaje GPT-4 mini que compacte el LaTeX
        prompt = f"""Compacta en texto plano la siguiente lista de expresiones
        matemáticas en LaTeX. Cada elemento de la lista es una expresión a compactar.
        Al final de cada compactación pon '<end>' obligatoriamente.
        Ejemplo: 
        Si la lista es ['d_1,\\ldots,d_(i-1)','d_(i+1),\\ldots,d_p']
        Devolver el string 'd₁, …, dᵢ₋₁<end>dᵢ₊₁, …, dₚ<end>'

        Lista a compactar: {latex_text}"""

        # Usar el modelo para generar la respuesta
        response = llm.invoke(prompt)
        response_content = dict(response)['content']
        return response_content
    except Exception as e:
        print(f"Error al procesar LaTeX: {e}")
        return latex_text

# Para compactar tablas
def compact_table(tables):
    try:
        # Solicitar al modelo de lenguaje GPT-4 mini que compacte el LaTeX
        prompt = f"Compacta en texto plano las siguientes tablas usando |, en caso de tener header mantener los nombres: {tables}. Sólo respondé con la compactación directa. Al final de cada compactación pon '<end>'"

        # Usar el modelo para generar la respuesta
        response = llm.invoke(prompt)
        response_content = dict(response)['content']
        return response_content.rstrip("\n\n")
    except Exception as e:
        print(f"Error al procesar la tabla: {e}")
        return tables

# Función principal para procesar el archivo y compactar los segmentos
def process_md_file(md_file_path, output_file_path):
    # Extrae los segmentos LaTeX
    latex_segments = extract_latex_segments(md_file_path)
    table_segments = extract_table_segments(md_file_path)
    
    # Compacta cada segmento y reemplázalo en el contenido original
    with open(md_file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    count = 0
    # tablas
    text = ''
    lista_tablas = []
    for segment in table_segments:
        #tokens = tokenizer.encode(text)
        token_count = len(text)
        # gemini tiene límite de tokens de output en aprox 8000,
        # por lo que pongo de umbral 20000 caracteres
        if token_count + len(segment) <= 4000:
            text += f'{segment}\n'
            lista_tablas.append(segment)
            if segment != table_segments[-1]:
                continue
        else:
            mantener = segment
        compacted = compact_table(text).split("<end>")
        if len(lista_tablas) <= len(compacted):
            for i in range(len(lista_tablas)):
                content = content.replace(f"{lista_tablas[i]}", f"{compacted[i]}")
        if mantener == '':
            lista_tablas = []
            text = ''
        else:
            lista_tablas = [mantener]
            text = f'{mantener}\n'
            mantener = ''
        count += 1

    # fórmulas
    lista_latex = []
    len_lista_latex = 0
    mantener = ''
    for i,latex in enumerate(latex_segments):
        # gemini tiene límite de tokens de output en aprox 8000,
        # Hay que jugar con el umbral para que el llm entienda todo el mensaje
        # y pueda actuar eficientemente. Propongo un umbral de 3000.
        # la contra es que aumenta las request.
        if len_lista_latex + len(latex) <= 1000:
            lista_latex.append(latex)
            len_lista_latex += len(latex)
            if i != len(latex_segments)-1:
                continue
        else:
            mantener = latex
        compacted = compact_latex(repr(lista_latex))
        lista_compactada = compacted.split("<end>")
        # Asegurar que cada compactación se hizo
        if len(lista_latex) <= len(lista_compactada):
            for i in range(len(lista_latex)):
                content = content.replace(f"${lista_latex[i]}$", f"{lista_compactada[i]}").replace("ï¼Œ", ",")
        if mantener == '':
            lista_latex = []
            len_lista_latex = 0
        else:
            lista_latex = [mantener]
            len_lista_latex = len(mantener)
            mantener = ''
        count += 1
    print('Cantidad total de requests hechas:',count)
    # Guarda el nuevo contenido con los LaTeX compactados
    with open(output_file_path, 'w', encoding='utf-8') as file:
        file.write(content)

# Ruta al archivo markdown de entrada y salida
md_file_path = 'probando.md'
output_file_path = 'archivo_salida.md'

# Procesa el archivo
process_md_file(md_file_path, output_file_path)

print("Archivo procesado con éxito.")
