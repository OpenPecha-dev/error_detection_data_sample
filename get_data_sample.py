import re
from typing import DefaultDict
import yaml
from pathlib import Path


def get_syls(text):
    chunks = re.split('(་|།།|།)',text)
    syls = []
    cur_syl = ''
    for chunk in chunks:
        if re.search('་|།།|།',chunk):
            cur_syl += chunk
            syls.append(cur_syl)
            cur_syl = ''
        else:
            cur_syl += chunk
    if cur_syl:
        syls.append(cur_syl)
    return syls

def get_context(chunk, type_):
    context = ''
    if ':' in chunk and type_ == 'left':
        context = re.search(':(.*)', chunk).group(1)

    else:
        syls = get_syls(chunk)
        if len(syls) >= 2:
            if type_ == 'left':
                context = f"{''.join(syls[-2:])}"
            else:
                context = f"{''.join(syls[:2])}"
        else:
            context = chunk
    return context.strip()

def get_note_sample(prev_chunk, chunk, next_chunk):
    note_sample = ''
    prev_context = get_context(prev_chunk, type_= 'left')
    next_context = get_context(next_chunk, type_= 'right')
    chunk = re.sub('\(\d+\) ', '', chunk)
    note_sample = f'{prev_context}{chunk}{next_context}'
    return note_sample

def parse_notes(collated_text):
    cur_text_notes = []
    chunks = re.split('(\(\d+\) <.+?>)', collated_text)
    prev_chunk = chunks[0]
    for chunk_walker, chunk in enumerate(chunks):
        try:
            next_chunk = chunks[chunk_walker+1]
        except:
            next_chunk = ''
        if re.search('\(\d+\) <.+?>', chunk):
            note_sample = get_note_sample(prev_chunk, chunk, next_chunk)
            cur_text_notes.append(note_sample)
            continue
        prev_chunk = chunk
    return cur_text_notes

def get_notes_samples(collated_text, note_samples, text_id):
    collated_text = collated_text.replace('\n', '')
    collated_text = re.sub('\d+-\d+', '', collated_text)
    cur_text_notes = parse_notes(collated_text)
    for cur_text_note in cur_text_notes:
        if note_samples.get(cur_text_note, {}):
            note_samples[cur_text_note]['count'] += 1
            note_samples[cur_text_note]['text_id']=text_id
        else:
            note_samples[cur_text_note] = DefaultDict()
            note_samples[cur_text_note]['count'] = 1
            note_samples[cur_text_note]['text_id']=text_id
    return note_samples

if __name__ == "__main__":
    note_samples = {}
    collated_text_paths  = list(Path('./collated_text').iterdir())
    collated_text_paths.sort()
    for collated_text_path in collated_text_paths:
        collated_text = collated_text_path.read_text(encoding='utf-8')
        text_id = collated_text_path.stem
        note_samples = get_notes_samples(collated_text, note_samples, text_id)
        print(f'{collated_text_path.stem} completed..')
    data_samples = {}
    for note, note_info in note_samples.items():
        data_samples[note] = dict(note_info)

    note_samples_yml = yaml.safe_dump(data_samples, default_flow_style=False,sort_keys=False,allow_unicode=True)
    Path('./data_samples.yml').write_text(note_samples_yml, encoding='utf-8')
