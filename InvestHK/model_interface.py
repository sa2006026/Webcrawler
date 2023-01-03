# from .IVHKCrawler import *
from .IVHKModel import *
from .config import CFG
from pathlib import Path


def train_new_model(model_type: str, texts: list[str], labels: list[int], save_to_path: str) -> dict:
    """
    Train a new investment leads model of type <model_type>
    And save it to a NEW folder.
    If folder that already exists is given, will raise an Error.

    Parameters
    ----------
    model_type : ('Deberta' | 'Bert' | 'Roberta')
        Type of model to use.
    
    texts : list[str]
        Input texts used as training data.
    
    labels : list[(0 | 1)]
        Input labels, 1 for positive samples, 0 for negatives.

    save_to_path : str
        Folder path to save trained model.

    Returns
    -------
    dict
        Evalution metrics of trained model.

    Sample Output
    -------
    {
        'f1_score': 0.12345, 
        'accuracy': 0.12345, 
        'AUC': 0.12345, 
        'runtime': 0.02312,
        'samples_per_second':184.05,
        'steps_per_second':46.0142,
        'epoch':4.0,
            
    }
        \nF1-score & Accuracy mesures model's ability of classifying single news.
        \nAUC mesures model's ability of comparing among different news.

    """
    save_to_path = Path(save_to_path)
    save_to_path.mkdir(exist_ok=False, parents=True)
    
    tokenizer = init_tokenizer(model_type)
    k_datasets = get_k_encoded_datasets(texts, labels, tokenizer, CFG.NUM_K_FOLDS)
    result = train_and_save(model_type, tokenizer, k_datasets, save_to_path)
    
    return result

def predict_score(model_path: str, texts: list[str]) -> list[float]:
    """
    Predict score of Investment leads with given model. 

    Parameters
    ----------
    model_path : str
        Local path to model folder.
    
    texts : list[str]
        Input texts to predict score of Investment leads.

    Returns
    -------
    list[float]
        Investment leads score of input texts. Range from 0.0 to 1.0 .
    
    Sample Output
    -------
    [0.01, 0.58, 0.77, 0.95]

    """
    
    return load_and_predict(Path(model_path), texts)


def get_sentiments(texts: list[str]) -> list[dict]:
    """
    Get financial sentiment analysis of given texts.

    Parameters
    ----------
    texts : list[str]
        Input texts to get financial sentiment analysis.

    Returns
    -------
    list[dict]
        Financial sentiment scores of each input text.

    Sample Output
    -------
    [ { 'positive': 0.3, 'neutral': 0.6, 'negative': 0.1 },
      { 'positive': 0.2, 'neutral': 0.3, 'negative': 0.5 } ]
        \nThree sentiment scores always add up to 1.0 .
    """
    return get_sentiment_infos(texts)


def get_entities(texts: list[str]) -> list[dict]:
    """
    Get named entity analysis of given texts.

    Parameters
    ----------
    texts : list[str]
        Input texts to get named entity analysis.

    Returns
    -------
    list[dict]
        Named entity informations of each input text.

    Sample Output
    -------
    [[Entity0, Entity1,... ], 
     [Entity0, Entity1,... ]]
    
    Each Entity is a python Dict:\n
    {
        'type': '(ORG | PER | LOC | MISC)',
        'name': 'Example (Organization | Person | Location | Miscellanrous Entity) Name',
        'start': 0,
        'end': 1,
        #Start & End Position in Text
    }

    """
    return get_entities_infos(texts)


