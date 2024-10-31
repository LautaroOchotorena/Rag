import fitz
import matplotlib.patches as patches
import matplotlib.pyplot as plt
from PIL import Image


def plot_pdf_with_boxes(pdf_page, segments):
    pix = pdf_page.get_pixmap()
    pil_image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    fig, ax = plt.subplots(1, figsize=(10, 10))
    ax.imshow(pil_image)
    categories = set()
    category_to_color = {
        "Title": "orchid",
        "Image": "forestgreen",
        "Table": "tomato",
    }
    for segment in segments:
        points = segment["coordinates"]["points"]
        layout_width = segment["coordinates"]["layout_width"]
        layout_height = segment["coordinates"]["layout_height"]
        scaled_points = [
            (x * pix.width / layout_width, y * pix.height / layout_height)
            for x, y in points
        ]
        box_color = category_to_color.get(segment["category"], "deepskyblue")
        categories.add(segment["category"])
        rect = patches.Polygon(
            scaled_points, linewidth=1, edgecolor=box_color, facecolor="none"
        )
        ax.add_patch(rect)

    # Make legend
    legend_handles = [patches.Patch(color="deepskyblue", label="Text")]
    for category in ["Title", "Image", "Table"]:
        if category in categories:
            legend_handles.append(
                patches.Patch(color=category_to_color[category], label=category)
            )
    ax.axis("off")
    ax.legend(handles=legend_handles, loc="upper right")
    plt.tight_layout()
    plt.show()

def render_page(doc_list: list, page_number: int, print_text=True) -> None:
    pdf_page = fitz.open(file_path).load_page(page_number - 1)
    page_docs = [doc for doc in doc_list if doc["metadata"].get("page_number") == page_number]
    segments = [doc["metadata"] for doc in page_docs]
    plot_pdf_with_boxes(pdf_page, segments)
    if print_text:
        for doc in page_docs:
            print(f"{doc.page_content}\n")


file_path = "E:\Lautaro Personal\Videos Facultad, Cursos y Clases de Canto y Musica\Proyectos\LangChain\docs\Análisis de datos multivariantes - Daniel Peña.pdf"

# Datos de ejemplo para `doc_list`
doc_list = [
    {
        "metadata": {
            "page_number": 1,
            "category": "Title",
            "coordinates": {
                "points": [(50, 750), (550, 750), (550, 700), (50, 700)],
                "layout_width": 600,
                "layout_height": 800
            }
        },
        "page_content": "Este es el título del documento"
    },
    {
        "metadata": {
            "page_number": 1,
            "category": "Image",
            "coordinates": {
                "points": [(100, 500), (300, 500), (300, 400), (100, 400)],
                "layout_width": 600,
                "layout_height": 800
            }
        },
        "page_content": "Descripción de una imagen en el documento"
    },
    {
        "metadata": {
            "page_number": 1,
            "category": "Table",
            "coordinates": {
                "points": [(50, 300), (550, 300), (550, 200), (50, 200)],
                "layout_width": 600,
                "layout_height": 800
            }
        },
        "page_content": "Datos de una tabla"
    }
]

render_page(doc_list, 1)