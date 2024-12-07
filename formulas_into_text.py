import re
import config_api_key
from langchain_google_genai import ChatGoogleGenerativeAI
import ast
import random

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
        prompt = r"""Compacta en texto plano la siguiente lista de expresiones
        matemáticas en LaTeX. Las expresiones están enumeradas.
        Aunque cada línea dentro de la expresión defina un cálculo diferente ponlo todo en la compactación.
        Si dos expresiones parecen conectarse considerarlas como separadas.
        Si una expresión tiene "\\\\" no considerar como dos o más expresiones.
        Al final de cada compactación pon '<end>' obligatoriamente salvo en el último elemento.
        Ejemplo: 
        Si la lista es
        "
        1) d_1,\\ldots,d_(i-1)
        2) d_(i+1),\\ldots,d_p
        "
        Se tiene que devolver "d₁, …, dᵢ₋₁<end>dᵢ₊₁, …, dₚ"

        Otro ejemplo:
        Si la lista es
        "
        1) \\begin{aligned}\nE(Y_{0i})&=40 \\\\\n&=60-20\\end{aligned}\\\\\n&=20*2
        2) 40=20+20
        "
        Se tiene que devolver "E(Y₀ᵢ)&=40\n&=60-20\n&=20*2<end>40=20+20"

        Importante: el número de expresiones tiene que coincidir con el número de compactaciones.
        Ejemplo: si se pasaron 5 expresiones se tienen que devolver 5 compactaciones.
        """
        # Otro ejemplo:
        # Si la lista es ['\\begin{aligned}\n&s_{11} =\\frac{1}{4}\\sum_{j=1}^{4}\\left(x_{j1}-\\overline{x}_{1}\\right)^{2}  \\\\\n&=\\frac{1}{4}((42-50)^{2}+(52-50)^{2}+(48-50)^{2}+(58-50)^{2})=34']
        # Devolver el string 's₁₁ = ¼Σ⁴ⱼ₌₁ (xⱼ₁ - x̄₁)² = ¼((42-50)²+(52-50)²+(48-50)²+(58-50)²) = 34'
        prompt = prompt + f"""

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
        
        resultado = "".join([f"{i + 1}) {item}\n" if i != len(latex_segments) - 1 else f"{i + 1}) {item}" for i, item in enumerate(lista_latex)])
        compacted = compact_latex(resultado)
        lista_compactada = compacted.rstrip('\n').split("<end>")
        if len(lista_latex) < len(lista_compactada):
            print('TENGO MENOS\n')
            print('lista:',lista_latex)
            print('\n\nLista compactada:', lista_compactada, '\n\n\n\n\n\n')
            if lista_compactada[-1] == '':
                lista_compactada.pop() # Elimina el último elemento
        if len(lista_latex) > len(lista_compactada):
            print('TENGO MAS\n')
            print('lista:',lista_latex)
            print('\n\nLista compactada:', lista_compactada, '\n\n\n\n\n\n')
        # Asegurar que cada compactación se hizo
        if len(lista_latex) <= len(lista_compactada):
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

# Ruta al archivo markdown de entrada y salida
md_file_path = 'probando.md'
output_file_path = 'archivo_salida.md'

# Procesa el archivo
process_md_file(md_file_path, output_file_path)

print("Archivo procesado con éxito.")
