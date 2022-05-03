import csv

from rank_options import OptionsRanker

def get_max_rank_pub(data, ranks):
    top_rank_note = ranks[0][0]
    if data[3] == top_rank_note:
        return "D"
    elif data[4] == top_rank_note:
        return "C"
    elif data[11][:-1] == top_rank_note:
        return "P"
    else:
        return "N"  

def reformat_options(options, right_context):
    peking_note = options[2][:-1]
    chone_note = options[3][:-1]
    if right_context[0] != "།":
        peking_note += "་"
        chone_note += "་"
    options[2] = peking_note
    options[3] = chone_note
    return options

def is_long(options):
    for option in options:
        if len(option)>50:
            return True
    return False
    
def get_updated_data(data, ranker):
    left_context = data[2]
    options = [data[3], data[4], data[11], data[12]]
    right_context = data[13]
    if is_long(options):
        return data
    ranks = ranker.rank(options=options, left_context=left_context, right_context=right_context)
    best_pub = get_max_rank_pub(data, ranks)
    data[5] = best_pub
    return data

def fill_probability():
    pre_data_sample = open("./pre_ludup_data_samples.csv")

    sample_csvreader = csv.reader(pre_data_sample)

    data_samples = []
    for row in sample_csvreader:
        data_samples.append(row)

    new_data_samples = []
    ranker = OptionsRanker()
    for data in data_samples[1:]:
        try:
            new_data = get_updated_data(data, ranker)
        except:
            new_data = data
        new_data_samples.append(new_data)
    output_path =f"./post_ludup_data_sample.csv"
    header = ["S.no", 'ཐག་གཅོད།་', "Left context", 'སྡེ།', 'ཅོ།', "prob", "Typo?",	"Sim","Rule","Decisions","Keep?", 'པེ།', 'སྣར།', 'Right context', 'ལེགས་སྦྱར།', 'བརྡ་རྙིང་།', 'བརྡ་གསར།', 'ལྡབ་ལོག།', "Frequency", "Src Text"]
    with open(output_path, "w", encoding="UTF8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(new_data_samples)

if __name__ == "__main__":
    fill_probability()