import re
import json
from unstructured.partition.pdf import partition_pdf

# from .generate import summarize_image, summarize_table

def find_midpoint(points):
    """
    Calculates the midpoint from the coordinates of a quadrilateral.
    """
    x_coords = [p[0] for p in points]
    y_coords = [p[1] for p in points]
    return sum(x_coords) / len(x_coords), sum(y_coords) / len(y_coords)

def calculate_distance(point1, point2) -> float:
    """
    Calculates the distance between two points.
    """
    return ((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2) ** 0.5

def match_image_to_captions(image, captions, category):
    """
    Matches items (figures or tables) with their captions based on proximity and page number.
    """
    image_midpoint = find_midpoint(image.metadata.coordinates.points)
    closest_caption = None
    closest_distance = float('inf')
    for caption in captions:
        # ページ番号が一致し、キャプションが図より下にあるか確認
        if image.metadata.page_number == caption.metadata.page_number and \
            find_midpoint(caption.metadata.coordinates.points)[1] > image_midpoint[1]:
            caption_midpoint = find_midpoint(caption.metadata.coordinates.points)
            distance = calculate_distance(image_midpoint, caption_midpoint)
            if distance < closest_distance:
                closest_distance = distance
                closest_caption = caption
    if closest_caption is not None:
        return closest_caption.text
    else:
        return None

def summarize_pdf(filename):
    """
    Extracts images and their captions from a given PDF file.

    :param filename: The path to the PDF file.
    :return: A tuple containing two lists - the first for images and the second for captions.
    """
    elements = partition_pdf(
        filename=pdf_path,
        strategy="hi_res",
        extract_images_in_pdf=True,
        extract_image_block_types=["Image", "Table"],
        extract_image_block_to_payload=False,
        extract_image_block_output_dir="./out/images",
        languages=["jpn", "eng"]  # Add other languages as needed
    )

    captions = [el for el in elements if el.category == "FigureCaption" or el.text.lower().startswith(("figure", "fig"))]

    text = []

    for elem in elements:
        if elem.category in ['Image', 'Table']:
            caption = match_image_to_captions(elem, captions, elem.category)
            if elem.category == 'Image':
                # response = summarize_image(elem)
                if caption is None:
                    text.append(f"\n図: {elem.text}\n")
                else:
                    text.append(f"\n図のタイトル: {caption}\n図: {elem.text}\n")
            else:
                # response = summarize_table(elem)
                if caption is None:
                    text.append(f"\n表: {elem.text}\n")
                else:
                    text.append(f"\n表のタイトル: {caption}\n表: {elem.text}\n")
        elif elem.category in ['NarrativeText', 'Title']:
            text.append(f"\n{elem.text}")

    return ''.join(text)


def save_output_to_file(output, file_path):
    """Saves the output JSON to a file."""
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(output)

if __name__ == "__main__":
    pdf_path = "./unstructured-test/2402.12352.pdf"
    output_file_path = './out/matched_figures_captions.md'

    text = summarize_pdf(pdf_path)

    save_output_to_file(
        text,
        output_file_path
    )
