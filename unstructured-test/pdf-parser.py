import re
import json
from unstructured.partition.pdf import partition_pdf

def extract_elements_from_pdf(pdf_path: str) -> dict:
    """
    Extracts text, tables, and figures from a given PDF file.

    :param pdf_path: The path to the PDF file.
    :return: A dictionary containing the extracted text, tables, and figures.
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

    text_elements = [el for el in elements if el.category == "Title" or el.category == "NarrativeText"]
    table_elements = [el for el in elements if el.category == "Table"]
    figure_elements = [el for el in elements if el.category == "Image"]
    caption_elements = [el for el in elements if el.category == "FigureCaption" or el.text.lower().startswith(("figure", "fig"))]

    return {
        "text": text_elements,
        "tables": table_elements,
        "figures": figure_elements,
        "captions": caption_elements
    }

def find_midpoint(points):
    """Calculates the midpoint from the coordinates of a quadrilateral."""
    x_coords = [p[0] for p in points]
    y_coords = [p[1] for p in points]
    return sum(x_coords) / len(x_coords), sum(y_coords) / len(y_coords)

def calculate_distance(point1, point2) -> float:
    """Calculates the distance between two points."""
    return ((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2) ** 0.5

def match_items_to_captions(items, captions, item_type="Image"):
    """Matches items (figures or tables) with their captions based on proximity and page number."""
    matches = []
    for item in items:
        item_midpoint = find_midpoint(item.metadata.coordinates.points)
        closest_caption, closest_distance = None, float('inf')
        for caption in captions:
            if item.metadata.page_number == caption.metadata.page_number:
                caption_midpoint = find_midpoint(caption.metadata.coordinates.points)
                is_caption = (item_type == "Image" and caption_midpoint[1] > item_midpoint[1]) or \
                            (item_type == "Table" and caption_midpoint[1] < item_midpoint[1])
                if is_caption:
                    distance = calculate_distance(item_midpoint, caption_midpoint)
                    if distance < closest_distance:
                        closest_distance, closest_caption = distance, caption
        matches.append((item.id, closest_caption.id if closest_caption else None))
    return matches

def extract_item_name(caption_text, item_type="Image"):
    """Extracts the item name (figure or table) from the caption text."""
    match = re.search(rf'^(fig|figure|tab|table|図|写真|表)\s*(\d+)', caption_text, re.IGNORECASE)
    return f"{item_type} {match.group(2)}" if match else f"Unknown {item_type}"

def create_output_json(matches, items, captions, item_type="Image"):
    """Creates a list of dictionaries representing the matched items and captions."""
    output = []
    for item_id, caption_id in matches:
        item = next((el for el in items if el.id == item_id), None)
        caption = next((el for el in captions if el.id == caption_id), None)

        if item and item.category == item_type:
            item_name = extract_item_name(caption.text if caption else "", item_type)
            caption_text = caption.text if caption else "No Caption"
            output.append({
                "id": item.id,
                "category": item.category,
                "name": item_name,
                "caption": caption_text,
                "item_path": item.metadata.image_path,
                "item_text": item.text,
            })
    return output

def create_text_json(items):
    """Creates a list of dictionaries representing the text."""
    output = []
    for item in items:
        output.append({
            "id": item.id,
            "text": item.text,
            "category": item.category,
            "page_number": item.metadata.page_number,
            "parent_id": item.metadata.parent_id,
            "file_directory": item.metadata.file_directory,
            "filename": item.metadata.filename,
        })
    return output

def save_output_to_file(output, file_path):
    """Saves the output JSON to a file."""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    pdf_path = "./unstructured-test/2402.12352.pdf"
    output_file_path = './out/matched_figures_captions.json'

    elements = extract_elements_from_pdf(pdf_path)
    text, tables, images, captions = elements['text'], elements['tables'], elements['figures'], elements['captions']

    image_matches = match_items_to_captions(images, captions, item_type="Image")
    table_matches = match_items_to_captions(tables, captions, item_type="Table")

    images_output_json = create_output_json(image_matches, images, captions, item_type="Image")
    tables_output_json = create_output_json(table_matches, tables, captions, item_type="Table")

    texts_output_json = create_text_json(text)

    save_output_to_file(
        {
            "text": texts_output_json,
            "images": images_output_json,
            "tables": tables_output_json
        },
        output_file_path
    )
