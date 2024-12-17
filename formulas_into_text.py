import re
import config_api_key
from langchain_google_genai import ChatGoogleGenerativeAI
import random
import os

# Función para detectar segmentos LaTeX en un archivo .md
def extract_latex_segments(md_file_path,content):
    # Se trató de hacer con un findall $...$ pero trae errores al considerar por ejemplo
    # "$5000" y "\$200".
    first_segment = content.split('$')
    # Filtra solo los segmentos que tienen contenido "\" que indica los segmentos de latex
    return [segment for segment in first_segment if ("\\" or "=") in segment]

def extract_table_segments(md_file_path, content):
    table_segments = re.findall(r'<table.*?>.*?</table>', content, re.DOTALL)
    
    # Filtra solo los segmentos que tienen contenido (ignora las tuplas vacías)
    return [segment for segment in table_segments if segment.strip()]

llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0)   

# Función para enviar el segmento a un modelo LLM para compactar
def compact_latex(latex_text):
    try:
        # Solicitar al modelo de lenguaje GPT-4 mini que compacte el LaTeX
        prompt = r"""Compact into plain text the following list of mathematical expressions in LaTeX.
        The expressions are delimited by "i) expression<end>" where i is a number.
        Even if each line within the expression defines a different calculation, include everything in the same compacted form.
        If two or more expressions seem connected, treat them as separate.
        If an expression contains "\\", do not consider it as two or more expressions.
        At the end of each compacted form, always include <end> except for the last element.
        If there's text involded keep it as it is.

        Example:
        If the list is
        "1) d_1,\\ldots,d_(i-1)<end>2) d_(i+1),\\ldots,d_p<end>"
        The result should be:
        "d₁, …, dᵢ₋₁<end>dᵢ₊₁, …, dₚ"

        Important: The number of compacted expressions must match the number of input expressions.
        For example, if 5 expressions are provided, 5 compacted forms must be returned.
        """
        # Otro ejemplo:
        # If the list is
        # "
        # 1) \\begin{aligned}\nE(Y_{0i})&=40 \\\\\n&=60-20\\end{aligned}\\\\\n&=20*2
        # 2) 40=20+20
        # "
        # The result should be: "E(Y₀ᵢ)&=40\n&=60-20\n&=20*2<end>40=20+20"
        prompt = prompt + f"""

        List to compact: {latex_text}"""

        # Usar el modelo para generar la respuesta
        response = llm.invoke(prompt)
        response_content = dict(response)['content']
        return response_content
    except Exception as e:
        print(f"Error al procesar LaTeX: {e}")
        return latex_text
def compact_latex_unit(latex_text):
    try:
        # Solicitar al modelo de lenguaje GPT-4 mini que compacte el LaTeX
        prompt = r"""Compact the following mathematical expression in LaTeX into plain text.
        At the end of the compacted form, include "<end>".
        If there's text involded keep it as it is.

        Example:
        If the input is:
        "1) d_1,\\ldots,d_(i-1),d_(i+1),\\ldots,d_p<end>"
        The result should be:
        "d₁, …, dᵢ₋₁,dᵢ₊₁, …, dₚ<end>"
        """
        prompt = prompt + f"""

        List to compact: {latex_text}"""

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
        prompt = f"""Compact the following tables into plain text using '|'.
        If there is a header, keep the column names: {tables}.
        Only respond with the direct compacted form.
        At the end of each compacted table, include '<end>''."""

        # Usar el modelo para generar la respuesta
        response = llm.invoke(prompt)
        response_content = dict(response)['content']
        return response_content.rstrip("\n\n")
    except Exception as e:
        print(f"Error al procesar la tabla: {e}")
        return tables

# Función principal para procesar el archivo y compactar los segmentos
def process_md_file(md_file_path, output_file_path):
    # Compacta cada segmento y reemplázalo en el contenido original
    with open(md_file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    content = content.replace('\\\\','\n')
    # Extrae los segmentos LaTeX
    latex_segments = extract_latex_segments(md_file_path, content)
    table_segments = extract_table_segments(md_file_path, content)
    
    count = 0
    # tablas
    text = ''
    lista_tablas = []
    mantener = ''
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
        elif segment == table_segments[-1]:
            text += f'{segment}'
            lista_tablas.append(segment)
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
    # al randomizar la lista genero que la llm no detecte conexiones entre segmentos
    # y los una cuando no quiero que se unan
    random.shuffle(latex_segments)
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
        elif i == len(latex_segments)-1:
            lista_latex.append(latex)
            len_lista_latex += len(latex)
        else:
            mantener = latex
        
        resultado = "".join([f"{i + 1}) {item}<end>" for i, item in enumerate(lista_latex)])
        compacted = compact_latex(resultado)
        lista_compactada = compacted.rstrip('\n').split("<end>")
        if len(lista_latex) < len(lista_compactada):
            if lista_compactada[-1] == '':
                lista_compactada.pop() # Elimina el último elemento
        if len(lista_latex) < len(lista_compactada) or len(lista_latex) > len(lista_compactada):
            lista_compactada = []
            for i in range(len(lista_latex)):
                lista_compactada.append(compact_latex_unit(f"{lista_latex[i]}").rstrip('\n').split('<end>')[0])
            print('lista:',lista_latex)
            print('\n\nLista compactada:', lista_compactada, '\n\n\n\n\n\n')
        # Asegurar que cada compactación se hizo
        if len(lista_latex) == len(lista_compactada):
            for i in range(len(lista_latex)):
                content = content.replace(f"$${lista_latex[i]}$$", f"{lista_compactada[i]}").replace(f"${lista_latex[i]}$", f"{lista_compactada[i]}").replace("ï¼Œ", ",")
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

md_directory = './md/merged_files'
# Ruta al archivo markdown de entrada y salida
for filename in os.listdir(md_directory):
    if filename.endswith(".md"):
        # Process the file
        process_md_file(md_directory + "/" + filename, f"final_md/{filename}")
        print(f"File {filename} processed successfully")
