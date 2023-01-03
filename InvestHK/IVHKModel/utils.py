import os
import shutil
import json
from itertools import cycle
from pathlib import Path

import torch
import pandas as pd
import numpy as np
import sklearn
import zhconv
from transformers import AutoModelForSequenceClassification, AutoTokenizer, TrainingArguments, Trainer
from transformers import pipeline
from datasets import Dataset, DatasetDict

from ..config import CFG


type2model  = {
        'Bert': 'bert-base-uncased',
        'Roberta': 'roberta-base',
        'Deberta': 'microsoft/deberta-v3-base',
        'Chinese': 'hfl/chinese-roberta-wwm-ext',
}

def init_tokenizer(model_type:str):
    return AutoTokenizer.from_pretrained(type2model[model_type])

def get_k_encoded_datasets(texts, labels, tokenizer, num_k_folds):

    ds = Dataset.from_dict({'text': texts,
                            'label': labels,})

    def process(u):
        return tokenizer(u['text'])
    
    encoded_ds = ds.map(process, batched=True)
    encoded_df = pd.DataFrame(encoded_ds)
    encoded_df['k'] = [k for (idx, k) in zip(range(len(encoded_df)), cycle(range(num_k_folds)))]
    k_split_dfs = [df for (idx, df) in encoded_df.groupby('k')]
    train_test_tuples = [(pd.concat(k_split_dfs[:k] + k_split_dfs[k+1:]), k_split_dfs[k]) for k in range(num_k_folds)]
    
    k_datasets = [DatasetDict({'train': Dataset.from_pandas(train),
                                'test': Dataset.from_pandas(test)
                                }) for (train, test) in train_test_tuples]
    return k_datasets


def cal_f1_auc(y, pred):
    
    precision, recall, thresholds =  sklearn.metrics.precision_recall_curve(y, pred)
    bestf1 = np.max(2*recall*precision/(recall+precision+1e-8))
    fpr, tpr, threhold = sklearn.metrics.roc_curve(y, pred)
    auc = sklearn.metrics.auc(fpr, tpr)
    return bestf1, auc

def compute_metrics(eval_pred):
    
    predictions, labels = eval_pred
    predictions = np.argmax(predictions, axis=1)
    bestf1, auc = cal_f1_auc(y=labels, pred=predictions)
    acc = (predictions == labels).mean()
    return {'f1_score': bestf1, 'AUC': auc, 'accuracy': acc}

def train_and_save(model_type, tokenizer, k_datasets, path:Path):
    
    origin_model = AutoModelForSequenceClassification.from_pretrained(type2model[model_type], num_labels=2)
    state_dict = origin_model.state_dict().copy()
    config = origin_model.config
    
    args = TrainingArguments(
                        path / 'trainning_record',
                        evaluation_strategy = "epoch",
                        save_strategy = "epoch",
                        learning_rate=CFG.LEARNING_RATE,
                        per_device_train_batch_size=CFG.TRAIN_BATCH_SIZE,
                        per_device_eval_batch_size=CFG.INFER_BATCH_SIZE,
                        num_train_epochs=CFG.NUM_EPOCHS,
                        weight_decay=CFG.WEIGHT_DECAY,
                        load_best_model_at_end=True,
                        metric_for_best_model=CFG.TARGET_METRIC,
                    )
    
    eval_results = []
    
    # Train with k folds
    for idx, ds in enumerate(k_datasets):
        model = AutoModelForSequenceClassification.from_config(config)
        model.load_state_dict(state_dict)
        
        trainer = Trainer(
        model,
        args,
        train_dataset=ds['train'],
        eval_dataset=ds['test'],
        tokenizer=tokenizer,
        compute_metrics=compute_metrics
        )
        
        trainer.train()
        eval_results.append(trainer.evaluate())
        model.save_pretrained(path / f'submodel_{idx}')
        del model, trainer
        torch.cuda.empty_cache()
    
    # Save tokenizer
    tokenizer.save_pretrained(path / "tokenizer")

    # Rearrange the directory
    shutil.copytree(path / 'trainning_record' / 'runs', path / 'runs')
    shutil.rmtree(path / 'trainning_record')
    
    # Output
    result_sheet = pd.DataFrame(eval_results)
    metrics = dict(result_sheet.mean())
    
    ret = {k[5:]:v for k,v in metrics.items() if k != 'epoch'}
    ret['epoch'] = metrics['epoch']
    
    # Dump output to json
    with open(path / "trainning_metrics.json", 'w+') as f:
        json.dump(ret, f)
    
    return ret

def load_and_predict(model_path, texts):
    
    tokenizer = AutoTokenizer.from_pretrained(model_path / "tokenizer")
    
    sub_folders = os.walk(model_path).__next__()[1]
    sub_folders = [folder for folder in sub_folders if folder.startswith("submodel")]
    sub_scores = []
    
    for folder in sub_folders:
        
        model = AutoModelForSequenceClassification.from_pretrained(model_path / folder)
        cls = pipeline("text-classification", model=model, tokenizer=tokenizer, return_all_scores=True,
                       device=0 if torch.cuda.is_available() else -1, batch_size=CFG.INFER_BATCH_SIZE)
        
        results = cls(texts, function_to_apply="softmax")
        predictions = [[d['score'] for d in result] for result in results]
        sub_scores.append(np.array(predictions)[:, 1])

    score = np.mean(sub_scores, axis=0).tolist()
    
    return score

from transformers import pipeline
import json


def get_entities_infos(texts):
    
    ner = pipeline('ner', model='dslim/bert-base-NER', aggregation_strategy='first',
                    device=0 if torch.cuda.is_available() else -1, batch_size=CFG.INFER_BATCH_SIZE)
    ner_infos = ner(texts)
    
    def _raw2output(info):
        return {
            'type': info['entity_group'],
            'name': info['word'],
            'start': info['start'],
            'end': info['end']
            }
    infos = [[_raw2output(info) for info in ner_info] for ner_info in ner_infos]
    
    return infos
    


def get_sentiment_infos(texts):
    
    cla = pipeline('text-classification', model='ProsusAI/finbert', return_all_scores=True, 
                    device=0 if torch.cuda.is_available() else -1, batch_size=CFG.INFER_BATCH_SIZE)
    sentiment_infos = cla(texts)
    
    def _raw2output(info):
        return {d['label']:d['score'] for d in info}
    
    infos = [_raw2output(info) for info in sentiment_infos]
    
    return infos

def get_translation_hk_en(texts):

    z2e = pipeline( "text2text-generation", model = "Helsinki-NLP/opus-mt-zh-en",
                    device=0 if torch.cuda.is_available() else -1, batch_size=CFG.INFER_BATCH_SIZE)
    
    zh_sentences = [zhconv.convert(s, 'zh-cn') for s in texts]
    z2e_output = z2e(zh_sentences)
    en_sentences = [r['generated_text'] for r in z2e_output]
    
    return en_sentences

def get_translation_en_zh(texts):

    e2z = pipeline( "text2text-generation", model = "Helsinki-NLP/opus-mt-en-zh",
                    device=0 if torch.cuda.is_available() else -1, batch_size=CFG.INFER_BATCH_SIZE)
    
    e2z_output = e2z(texts)
    zh_sentences = [r['generated_text'] for r in e2z_output]
    return zh_sentences

def get_translation_hk_zh(texts):
    
    return [zhconv.convert(s, 'zh-cn') for s in texts]

        
    
    
    
    