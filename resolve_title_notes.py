import re
import logging
from pathlib import Path

logging.basicConfig(filename="issue_text.log", level=logging.INFO, filemode="w")

def remove_title_notes(collated_text, text_id):
    notes = re.findall("\(\d+\) <.+?>", collated_text)
    try:
        title_note = notes[0]
        collated_text = collated_text.replace(title_note, "")
    except:

        logging.info(f"{text_id}")
        
    return collated_text


if __name__ == "__main__":
    collated_text_paths = list(Path('./collated_text').iterdir())
    collated_text_paths.sort()
    for collated_text_path in collated_text_paths:
        text_id = collated_text_path.stem
        collated_text = collated_text_path.read_text(encoding='utf-8')
        clean_collated_text = remove_title_notes(collated_text, text_id)
        Path(f'./collated_text_without_title_note/{text_id}.txt').write_text(clean_collated_text, encoding='utf-8')
        print(f'{text_id} completed ..')