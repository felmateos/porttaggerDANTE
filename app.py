import logging
import os
from pathlib import Path
from typing import List, Tuple

import gradio as gr
import pandas as pd
import spacy
import torch

from dante_tokenizer import DanteTokenizer

from transformers import AutoModelForTokenClassification, AutoTokenizer

from preprocessing import *

try:
    nlp = spacy.load("pt_core_news_sm")
except Exception:
    os.system("python -m spacy download pt_core_news_sm")
    nlp = spacy.load("pt_core_news_sm")
dt_tokenizer = DanteTokenizer()

default_model = "Tweets (stock market)"
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
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

class MyApp:
    def __init__(self) -> None:
        self.model = None
        self.tokenizer = None
        self.pre_tokenizer = None
        self.load_model()

    def load_model(self, model_name: str = default_model):
        if model_name not in model_choices.keys():
            logger.error("Selected model is not supported, resetting to the default model.")
            model_name = default_model
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


def batch_analysis_csv(input_file, id_column: str='tweet_id', content_column: str='content', prefix: str='dante_02', keep_replace_contraction=True):
    df = pd.read_csv(input_file.name, encoding='utf-8')
    ids = df[id_column]
    texts = df[content_column]
    texts = texts.replace(r'\\n', ' ', regex=True)
    texts = texts.apply(lambda x : x.strip())
    conllu_output = []

    for id, sent in zip(ids, texts):
        conllu_output.append("# sent_id = {}_{}\n".format(prefix, id))
        conllu_output.append("# text = {}\n".format(sent))
        tokens, labels, _ = predict(sent, logger)
        tokens_labels = list(zip(tokens, labels))

        for j, (token, label) in enumerate(tokens_labels):
            try:
                contr = tokens_labels[j][0] + ' ' + tokens_labels[j+1][0]
                for expansion in expansions.keys():
                    replace_str = expansions[expansion]
                    match = re.match(expansion, contr, re.I)
                    expansion = replace_keep_case(expansion, replace_str, contr)
                    if match is not None:
                        conllu_output.append("{}\t{}".format(str(j+1)+'-'+str(j+2), expansion) + "\t_" * 8 + "\n")
                        break
                conllu_output.append("{}\t{}\t_\t{}".format(j + 1, token, label) + "\t_" * 6 + "\n")
            except IndexError:
                conllu_output.append("{}\t{}\t_\t{}".format(j + 1, token, label) + "\t_" * 6 + "\n") 
        conllu_output.append("\n")
    output_filename = "output.conllu"
    with open(output_filename, "w", encoding='utf-8') as out_f:
        out_f.writelines(conllu_output)
    return {output_file: output_file.update(visible=True, value=output_filename)}


css = open("style.css").read()
top_html = open("top.html").read()
bottom_html = open("bottom.html").read()

with gr.Blocks(css=css) as demo:
    gr.HTML(top_html)
    select_model = gr.Dropdown(choices=list(model_choices.keys()), label="Tagger model", value=default_model)
    select_model.change(myapp.load_model, inputs=[select_model])
    
    id_column = gr.Textbox(placeholder='tweet_id', label='Id column')
    content_column = gr.Textbox(placeholder='content', label='Content column')
    label_prefix = gr.Textbox(placeholder='dante_02', label='Label prefix')

    with gr.Tab("Multiple sentences"):
        gr.HTML(
            """
        <p align="justify"">
        &emsp;Upload a plain text file with sentences in it. 
        Find below an example of what we expect the content of the file to look like. 
        Sentences are automatically split by spaCy's sentencizer. 
        To force an explicit segmentation, manually separate the sentences using a new line for each one.</p>
        """
        )
        gr.Markdown(
            """
        ```
        Então ele hesitou, quase como se estivesse surpreso com as próprias palavras, e recitou:
        – Vá e não tornes a pecar!
        Baley, sorrindo de repente, pegou no cotovelo de R. Daneel e eles saíram juntos pela porta.
        ```
        """
        )
        input_file = gr.File(label="Upload your input file here...")
        output_file = gr.File(label="Tagged file", visible=False)
        submit_btn_batch = gr.Button("Tag it")
        submit_btn_batch.click(
            fn=batch_analysis_csv, inputs=[input_file, id_column], outputs=output_file
        )

    gr.HTML(bottom_html)


demo.launch(debug=True)