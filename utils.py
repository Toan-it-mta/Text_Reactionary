import evaluate
import numpy as np
import re
from sklearn.metrics import f1_score
from datasets import Dataset
import pandas as pd
import os
from model_asr import Model_ASR

accuracy = evaluate.load("accuracy")

def compute_metrics_acc_score(eval_pred):
    predictions, labels = eval_pred
    predictions = np.argmax(predictions, axis=1)
    return accuracy.compute(predictions=predictions, references=labels)

def compute_metrics_f_score(eval_pred):
    predictions, labels = eval_pred
    predictions = np.argmax(predictions, axis=1)
    score = f1_score(labels,predictions, average='macro')
    return {"f1_score": float(score)}

def compute_metrics(eval_pred):
    # Tính toán và trả về độ đo hiệu suất từ nhiều hàm tính toán độ đo riêng lẻ
    metric_results = {}
    for metric_function in [compute_metrics_acc_score, compute_metrics_f_score]:
        metric_results.update(metric_function(eval_pred))
    return metric_results

def preprocessing_text(text):
    text = re.sub("\r", "\n", text)
    text = re.sub("\n{2,}", "\n", text)
    text = re.sub("…", ".", text)
    text = re.sub("\.{2,}", ".", text)
    text = text.strip()
    text = text.lower()
    return text

def load_train_valid_dataset(path_train_data:str, val_size:float):
    """
    Load bộ dữ liệu và chia train/valid
    Parameters
    ----------
    path_train_data : str , Đường dẫn tới file train.csv
    val_size : float , Tỷ lệ của tập Valid
    """
    df = pd.read_csv(path_train_data)
    del df['path']
    df = df[df['text'].notna()]
    df_valid = df.sample(frac=val_size)
    df_valid['text'] = df_valid['text'].apply(preprocessing_text)
    df_train = df.drop(df_valid.index)
    df_train['text'] = df_train['text'].apply(preprocessing_text)
    train_dataset = Dataset.from_pandas(df_train)
    valid_dataset = Dataset.from_pandas(df_valid)
    return train_dataset, valid_dataset
                
def get_text_from_file_mp3(path_file_mp4:str, model_asr: Model_ASR):
    text = model_asr.infer(os.path.join("./datasets",path_file_mp4))
    return text

def processing_dataset(path_dataset_csv:str, model_asr: Model_ASR):
    df = pd.read_csv(path_dataset_csv)
    df['text'] = df['path'].apply(lambda x: get_text_from_file_mp3(x, model_asr))
    df.to_csv(path_dataset_csv, index=False)

    