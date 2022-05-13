from pathlib import Path
from docx import Document
# from botok.thrid_party.has_skrt_syl import has_skrt_syl
from openpecha.utils import dump_yaml, load_yaml
from botok.third_party.has_skrt_syl import has_skrt_syl
import json
    
def get_highlighted_text(doc):
    highlights = []
    final_dic = {}
    texts = ""
    text = {}
    curr_text = {}
    para = {}
    all_paras = doc.paragraphs
    for para_num, paragraph in enumerate(all_paras,0):
        if len(paragraph.runs) == 1:
            continue
        else:
            for num, run in enumerate(paragraph.runs, 0):
                if has_skrt_syl(run.text):
                    sanskrit = True
                    texts += run.text
                else:
                    sanskrit = False
                    texts += run.text
                curr_text[num] = {
                    "len": len(run.text),
                    "text": run.text,
                    "sanskrit": sanskrit
                    }
                text.update(curr_text)
                curr_text = {}
            para[para_num] = {
                "info": text,
                "texts": texts
            }
            final_dic.update(para)
            text = {}
            texts = ""
            para = {}
    return final_dic
    
def parse_doc_for_skrt_with_context(doc_paths):
    for doc_path in doc_paths:
        doc = Document(Path(doc_path))
        dic = get_highlighted_text(doc)
        filename = doc_path.name[:-5]
        json_path = Path(f"./{filename}.yml")
        dump_yaml(dic, json_path)
        
def dump_json(dic, data_path):
    json_object = json.dumps(dic, sort_keys=True, ensure_ascii=False, indent=4)
    with open(f"{data_path}", "w") as outfile:
        outfile.write(json_object)

def from_json(file_path):
    json_file = file_path.read_text(encoding='utf-8')                    
    json_object = json.loads(json_file)
    return json_object

def get_num_of_sanskrit(part_infos):
    sanskrit_num = 0
    for _,info in part_infos.items():
        if info['sanskrit'] == True:
            sanskrit_num += 1
    return sanskrit_num

def get_span_of_part(part_infos, part_num):
    prev_end = 0
    if part_num == 0:
            return 0, part_infos[0]['len']
    else:
        for num, part in part_infos.items():
            if num != part_num:
                prev_end += part['len']
            elif num == part_num:
                start = prev_end
                end = start + part['len']
                return start, end
            

def create_training_data(file_paths):
    curr_json = {}
    data = []
    label = []
    for file_path in file_paths:
        # if "sanskrit_text_kangyur_v101.json" == file_path.name:
        #     continue
        yaml_file = load_yaml(file_path)
        for _, text_info in yaml_file.items():
            for num, part_info in text_info['info'].items():
                if part_info['sanskrit'] == True:
                    start, end = get_span_of_part(text_info['info'], num)
                    label.append([start, end])
                    # if num == 0:
                    #     start += 0
                        
                    # else:
                    #     start == end 
                    # end = start + part_info['len']
                    # label.append([start, end])
                # else:
                #     start = end + part_info['len']
                #     end = start
            curr_json={
                    "text": text_info['texts'],
                    "label": label
                }
            data.append(curr_json)
            curr_json = {}
            label = []
        filename = file_path.name[:-4]
        data_path = Path(f"./sanskrit-cluster/training_data/{filename}.json")
        dump_json(data, data_path)
    
if __name__ == "__main__":
    # cluster_paths = Path("./sanskrit-cluster/docs/").iterdir()
    # parse_doc_for_skrt_with_context(cluster_paths)
    file_paths = list(Path(f"./yml_of_text/").iterdir())
    # file_paths = [Path(f"./yml/test.yml")]
    create_training_data(file_paths)
