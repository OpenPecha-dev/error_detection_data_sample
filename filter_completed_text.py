from pathlib import Path


def parse_text_info(pedurma_text):
    text_infos = {}
    raw_text_infos = pedurma_text.split(',')
    if 'ཚར།' in raw_text_infos[3] and 'ཚར།' in raw_text_infos[7]:
        text_infos['status'] = True
    else:
        text_infos['status'] = False
    text_infos['text_id'] = raw_text_infos[1]
    return text_infos


def get_completed_text(pedurma_list):
    completed_text = []
    pedurma_texts = pedurma_list.splitlines()
    for pedurma_text in pedurma_texts:
        text_infos = parse_text_info(pedurma_text)
        if text_infos['status'] == True:
            completed_text.append(text_infos['text_id'])
    return completed_text

if __name__ == "__main__":
    pedurma_list = Path('./pedurma_list.txt').read_text(encoding='utf-8')
    completed_text = get_completed_text(pedurma_list)
    Path('./collated_text_list.txt').write_text("\n".join(completed_text), encoding='utf-8')