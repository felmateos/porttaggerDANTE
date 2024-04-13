import logging
import os
from typing import List, Tuple
import pandas as pd
import spacy
import torch
from dante_tokenizer import DanteTokenizer
from transformers import AutoModelForTokenClassification, AutoTokenizer
from dotenv import dotenv_values

from dante_tokenizer.data.preprocessing import split_monetary_tokens, normalize_text, split_enclisis
from preprocessing import *

try:
    nlp = spacy.load("pt_core_news_sm")
except Exception:
    os.system("python -m spacy download pt_core_news_sm")
    nlp = spacy.load("pt_core_news_sm")
dt_tokenizer = DanteTokenizer()

model_choices = {
    "News": "Emanuel/porttagger-news-base",
    "Tweets (stock market)": "Emanuel/porttagger-tweets-base",
    "Oil and Gas (academic texts)": "Emanuel/porttagger-oilgas-base",
    "Multigenre": "Emanuel/porttagger-base",
}
pre_tokenizers = {
    "News": nlp,
    "Tweets (stock market)": dt_tokenizer.tokenize,
    "Oil and Gas (academic texts)": nlp,
    "Multigenre": nlp,
}

env_vars = dotenv_values('.env')

for key, value in env_vars.items():
    globals()[key] = value

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

class MyApp:
    def __init__(self) -> None:
        self.model = None
        self.tokenizer = None
        self.pre_tokenizer = None
        self.load_model()

    def load_model(self, model_name: str = DEFAULT_MODEL):
        if model_name not in model_choices.keys():
            logger.error("Selected model is not supported, resetting to the default model.")
            model_name = DEFAULT_MODEL
        self.model = AutoModelForTokenClassification.from_pretrained(model_choices[model_name])
        self.tokenizer = AutoTokenizer.from_pretrained(model_choices[model_name])
        self.pre_tokenizer = pre_tokenizers[model_name]

myapp = MyApp()

def predict(text, logger=None) -> Tuple[List[str], List[str]]:
    doc = myapp.pre_tokenizer(text)
    tokens = [token.text if not isinstance(token, str) else token for token in doc]

    logger.info("Starting predictions for sentence: {}".format(text))
    print("Using model {}".format(myapp.model.config.__dict__["_name_or_path"]))

    input_tokens = myapp.tokenizer(
        tokens,
        return_tensors="pt",
        is_split_into_words=True,
        return_offsets_mapping=True,
        return_special_tokens_mask=True,
        
    )
    output = myapp.model(input_tokens["input_ids"])

    i_token = 0
    labels = []
    scores = []
    for off, is_special_token, pred in zip(
        input_tokens["offset_mapping"][0],
        input_tokens["special_tokens_mask"][0],
        output.logits[0],
    ):
        if is_special_token or off[0] > 0:
            continue
        label = myapp.model.config.__dict__["id2label"][int(pred.argmax(axis=-1))]
        if logger is not None:
            logger.info("{}, {}, {}".format(off, tokens[i_token], label))
        labels.append(label)
        scores.append(
            "{:.2f}".format(100 * float(torch.softmax(pred, dim=-1).detach().max()))
        )
        i_token += 1

    return tokens, labels, scores

def batch_analysis_csv(ID_COLUMN: str, CONTENT_COLUMN: str, DATA_PATH: str, PREFIX:str, OUTPUT_PATH: str, KEEP_REPLACE_CONTRACTION: bool):
    df = pd.read_csv(DATA_PATH)
    ids = df[ID_COLUMN]
    texts = df[CONTENT_COLUMN]
    texts = texts.replace(r'\\n', ' ', regex=True) # remover '\n' mas não por espaço
    texts = texts.apply(lambda x : x.strip()) # remover espaços excedentes
    conllu_output = []

    for id, sent in zip(ids, texts):
        conllu_output.append("# sent_id = {}_{}\n".format(PREFIX, id))
        conllu_output.append("# text = {}\n".format(sent))
        tokens, labels, _ = predict(sent, logger)
        tokens_labels = list(zip(tokens, labels))

        for j, (token, label) in enumerate(tokens_labels):
            try:
                contr = tokens_labels[j][0] + ' ' + tokens_labels[j+1][0]
                for expansion in expansions.keys():
                    replace_str = expansions[expansion]
                    match = re.match(expansion, contr, re.IGNORECASE)
                    expansion = replace_keep_case(expansion, replace_str, contr)
                    if match is not None:
                        conllu_output.append("{}\t{}".format(str(j+1)+'-'+str(j+2), expansion) + "\t_" * 8 + "\n")
                        break
                conllu_output.append("{}\t{}\t_\t{}".format(j + 1, token, label) + "\t_" * 6 + "\n")
            except IndexError:
                conllu_output.append("{}\t{}\t_\t{}".format(j + 1, token, label) + "\t_" * 6 + "\n")
        conllu_output.append("\n")
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as out_f:
        out_f.writelines(conllu_output)

def main():
    batch_analysis_csv(ID_COLUMN, CONTENT_COLUMN, DATA_PATH, PREFIX, OUTPUT_PATH, KEEP_REPLACE_CONTRACTION)

if __name__ == '__main__':
    main()