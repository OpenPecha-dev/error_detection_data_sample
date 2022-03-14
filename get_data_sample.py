import re
import csv
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
    chunk = chunk.replace(':', '')
    context = ''
    syls = get_syls(chunk)
    if len(syls) >= 4:
        if type_ == 'left':
            context = f"{''.join(syls[-4:])}"
        else:
            context = f"{''.join(syls[:4])}"
    else:
        context = chunk
    return context.strip()

def clean_note(note_text):
    noise_anns = ['«པེ་»', '«སྣར་»', '«སྡེ་»', '«ཅོ་»', '\(\d+\) ', ':']
    for noise_ann in noise_anns:
        note_text = re.sub(noise_ann, '', note_text)
    return note_text

def get_default_option(prev_chunk):
    default_option = ''
    if ':' in prev_chunk:
        default_option = re.search(':(.*)', prev_chunk).group(1)
    else:
        syls = get_syls(prev_chunk)
        if syls:
            default_option = syls[-1]
    return default_option

def get_note_options(default_option, chunk):
    chunk = re.sub('\(\d+\)', '', chunk)
    pub_mapping = {
        '«པེ་»': 'peking',
        '«པེ»': 'peking',
        '«སྣར་»': 'narthang',
        '«སྣར»': 'narthang',
        '«སྡེ་»': 'derge',
        '«སྡེ»': 'derge',
        '«ཅོ་»': 'chone',
        '«ཅོ»': 'chone'
    }
    note_options = {
        'peking': '',
        'narthang': '',
        'derge': '',
        'chone': ''
    }
    note_parts = re.split('(«པེ་»|«སྣར་»|«སྡེ་»|«ཅོ་»|«པེ»|«སྣར»|«སྡེ»|«ཅོ»)', chunk)
    pubs = note_parts[1::2]
    notes = note_parts[2::2]
    for walker, (pub, note_part) in enumerate(zip(pubs, notes)):
        if note_part:
            note_options[pub_mapping[pub]] = note_part.replace('>', '')
        else:
            if notes[walker+1]:
                note_options[pub_mapping[pub]] = notes[walker+1].replace('>', '')
            else:
                note_options[pub_mapping[pub]] = notes[walker+2].replace('>', '')
    if not note_options.get('derge', ''):
        note_options['derge'] = default_option
    if not note_options.get('narthang', ''):
        note_options['narthang'] = default_option
    if not note_options.get('peking', ''):
        note_options['peking'] = default_option
    if not note_options.get('chone', ''):
        note_options['chone'] = default_option
    return note_options

def get_note_sample(prev_chunk, chunk, next_chunk):
    note_sample = ''
    default_option = get_default_option(prev_chunk)
    prev_chunk = re.sub(f'{default_option}$', '', prev_chunk)
    prev_context = get_context(prev_chunk, type_= 'left')
    next_context = get_context(next_chunk, type_= 'right')
    note_options = get_note_options(default_option, chunk)
    note_options = dict(sorted(note_options.items()))
    note_sample = f'{prev_context}[{",".join(str(note) for note in note_options.values())}]{next_context}'
    return [note_sample, note_options]

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
            note_sample, note_options  = get_note_sample(prev_chunk, chunk, next_chunk)
            cur_text_notes.append([note_sample, note_options])
            continue
        prev_chunk = chunk
    return cur_text_notes

def get_notes_samples(collated_text, note_samples, text_id):
    collated_text = collated_text.replace('\n', '')
    collated_text = re.sub('\d+-\d+', '', collated_text)
    cur_text_notes = parse_notes(collated_text)
    for cur_text_note, note_options in cur_text_notes:
        if note_samples.get(cur_text_note, {}):
            note_samples[cur_text_note]['count'] += 1
            note_samples[cur_text_note]['text_id']=text_id
        else:
            note_samples[cur_text_note] = DefaultDict()
            note_samples[cur_text_note]['count'] = 1
            note_samples[cur_text_note]['text_id']=text_id
            note_samples[cur_text_note]['note_options'] = note_options
    return note_samples

def is_all_option_same(note_options):
    if note_options['derge'] == note_options['chone'] == note_options['peking'] == note_options['narthang']:
        return True
    else:
        return False

def get_note_context(note):
    right_context = ''
    left_context = ''
    if re.search(r'(.+)\[', note):
        left_context = re.search(r'(.+)\[', note).group(1)
    if re.search(r'\](.+)', note):
        right_context = re.search(r'\](.+)', note).group(1)
    return left_context, right_context

def get_sample_entry(note_walker, note, note_info):
    all_option_same_flag = is_all_option_same(note_info.get('note_options', {}))
    left_context, right_context = get_note_context(note)
    data_entry = [
        note_walker,
        '',
        left_context,
        note_info['note_options']['derge'],
        note_info['note_options']['chone'],
        note_info['note_options']['peking'],
        note_info['note_options']['narthang'],
        right_context,
        '',
        '',
        '',
        all_option_same_flag,
        note_info['count'],
        note_info['text_id'],
        ]
    return data_entry

def generate_csv_report(note_samples):
    output_path = f"./data_samples.csv"
    header = ["S.no", 'ཐག་གཅོད།་', "Left context", 'སྡེ།', 'ཅོ།', 'པེ།', 'སྣར།', 'Right context', 'ལེགས་སྦྱར།', 'བརྡ་རྙིང་།', 'བརྡ་གསར།', 'ལྡབ་ལོག།', "Frequency", "Src Text"]
    with open(output_path, "w", encoding="UTF8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for note_walker,(note, note_info) in enumerate(note_samples.items(),1):
            data = get_sample_entry(note_walker, note, note_info)
            writer.writerow(data)


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
    generate_csv_report(note_samples)
