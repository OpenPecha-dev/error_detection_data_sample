from docx import Document
from pathlib import Path
from botok.third_party.has_skrt_syl import has_skrt_syl




def get_highlighted_text():
    highlights = []
    texts = ""
    all_paras = doc.paragraphs
    for paragraph in all_paras:
        if len(paragraph.runs) == 1:
            continue
        else:
            for run in paragraph.runs:
                # if run.font.highlight_color:
                #     highlights.append(run.text)
                # if has_skrt_syl(run.text):
                texts += run.text
        highlights.append(texts)
        texts = ""
    return highlights


if __name__ == "__main__":
    
    doc_paths = Path("./sanskrit-cluster/docs/").iterdir()
    for num, doc_path in enumerate(doc_paths, 1):
        sanskrits = ""
        doc = Document(Path(doc_path))
        texts = get_highlighted_text()
        for text in texts:
            sanskrits += text+"\n"
        Path(f"sanskrit-cluster/cluster_list/cluster_with_context_{num:02}.txt").write_text(sanskrits, encoding='utf-8')
