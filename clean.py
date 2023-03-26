import re
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch
from torch.utils.data import Dataset, DataLoader

data_file = "cleaned_merged_fairy_tales_without_eos.txt"
STORIES = {}
POEM_AUTHORS = ['EDWARD LEAR', 'ISAAC WATTS', 'JANE TAYLOR', 'PHOEBE CARY', 'ANN TAYLOR', 'ANONYMOUS', 'CHARLES KINGSLEY', 'CHARLES MACKAY', 'CLEMENT CLARKE MOORE', 'DAVID EVERETT', 'ELIZA LEE FOLLEN', 'FELICIA DOROTHEA HEMANS', 'FELICIA DOROTHEA HEMANS', 'FELICIA DOROTHEA HEMANS', 'FRANCIS C. WOODWORTH', 'FROM M. DE LAMOTTE', 'GEORGE MACDONALD', 'HANNAH FLAGG GOULD', 'HENRY WADSWORTH LONGFELLOW', 'JAMES HOGG', 'JAMES MERRICK',
                'JAMES WHITCOMB RILEY', 'JANE TAYLOR', 'JEMIMA LUKE', 'LEWIS CARROLL', 'LITTLE B. (TAYLOR?)', 'LYDIA MARIA CHILD', 'MARY HOWITT', 'MARY HOWITT', 'MARY HOWITT', 'OLD CAROL', 'REGINALD HEBER', 'RICHARD MONCKTON MILNES (LORD HOUGHTON)', 'ROBERT BURNS', 'ROBERT LOUIS STEVENSON', 'ROBERT SOUTHEY', 'SABINE BARING-GOULD', 'THOMAS HOOD', 'WILLIAM BRIGHTY RANDS', 'WILLIAM HOWITT', 'WILLIAM ROBERT SPENCER', 'WILLIAM SHAKESPEARE', 'WILLIAM WORDSWORTH']


def clean_data():
    with open(data_file, "r") as f:
        lines = f.readlines()
        first_line = lines[0].strip(" \n")
        curr_title = re.sub('[\t]+', '', first_line).upper()
        for i in range(1, len(lines) - 1):
            line = lines[i].strip(" \n")
            line = re.sub('[\t]+', '', line)  # to remove tabs
            line = re.sub("        ", '', line)
            if len(line) == 0 or (line in POEM_AUTHORS):
                continue

            elif (line in ["CINDERELLA", "BLUE BEARD", "SUPPOSE!", "PRETTY COW", "THE OWL AND THE PUSSY-CAT"]):
                curr_title = line
                STORIES[curr_title] = []

            if (line == '\n' or len(line) < 3) and len(lines[i+1]) < 50:
                upcoming_title = lines[i+1].strip(" \n")
                curr_title = re.sub('[\t]+', '', upcoming_title).upper()

            elif (line[0].isnumeric()):
                curr_title = line.upper()
                STORIES[curr_title] = []

            elif (line.isupper() and " STORY" in lines[i+1]):
                first_sentence = lines[i+1].split()
                if "--" in curr_title:
                    # replace with next chapter
                    curr_title = curr_title.split(
                        " --", 1)[0] + " --" + ' '.join(first_sentence[0:2])
                else:
                    curr_title = line + " --" + ' '.join(first_sentence[0:2])

                STORIES[curr_title] = [' '.join(first_sentence[2:])]

            elif (" STORY" in line or " Story." in line) and not ("OF" in line and not (" STORY" in lines[i+1])):
                first_sentence = line.split()
                if "--" in curr_title:
                    # replace with next chapter
                    curr_title = curr_title.split(
                        " --", 1)[0] + " --" + ' '.join(first_sentence[0:2])
                else:
                    curr_title = curr_title + " --" + \
                        ' '.join(first_sentence[0:2])

                begin_story = [' '.join(first_sentence[2:])]
                if len(begin_story) <= 1:
                    STORIES[curr_title] = []
                else:
                    STORIES[curr_title] = [' '.join(first_sentence[2:])]

            elif (line.isupper()) and not (str(lines[i+1].split()[0:2]).isupper() or ("THE END" in line) or ("\"" in line) or ("“" in line) or ("\'" in line) or ("{" in line) or (line in "TRESPASSERS WILL BE PROSECUTED") or (line in "FAMOUS DONKEY THE STAR OF THE DANCE") or (line in "ADAPTED BY") or (line in "* A.D. 1482-1513")):
                if (len(line) >= 11 and len(line) < 50):
                    curr_title = line.upper()
                    STORIES[curr_title] = []

                elif (len(line) < 11 and len(line) < 50) or (line in "CHAPTER"):
                    if "--" in curr_title:
                        # replace with next chapter
                        curr_title = curr_title.split(
                            " --", 1)[0] + " --" + line
                    if not (line in curr_title):
                        curr_title = curr_title + " --" + line
                    STORIES[curr_title] = []

            elif (curr_title in STORIES) and (line.upper() != curr_title):
                STORIES[curr_title].append(line)
            else:
                STORIES[curr_title] = []

    # To finalize the cleaning: removes extra titles that never got fed in
    STORIES_COPY = STORIES.copy()
    for story in STORIES_COPY:
        if STORIES[story] == []:
            STORIES.pop(story)



clean_data()
num_stories = len(STORIES)

def create_test_set():
    # Creates a very small test set to compare generated text with the reality
    # Takes in the last 20 words for every song
    # TODO: To discuss with group
    # test_set = {}
    # for title in STORIES:
    #     test_set[title] = STORIES[title].str.split().str[-20:].apply(' '.join)
    pass


# Dataset comes from torch.utils.data
class Stories(Dataset):
    def __init__(self, control_code, truncate=False, gpt2_type="gpt2", max_length=1024):

        self.tokenizer = GPT2Tokenizer.from_pretrained(gpt2_type)
        self.stories = []

        for title in STORIES:
          self.stories.append(torch.tensor(
                self.tokenizer.encode(f"<|{control_code}|>{STORIES[title][:max_length]}<|endoftext|>")
            ))
        if truncate:
            self.stories = self.stories[:20000]
        self.stories_count = len(self.stories)
    def __len__(self):
        return self.lyrics_count

    def __getstory__(self, story):
        return self.stories[story]