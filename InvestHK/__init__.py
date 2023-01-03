from .model_interface import (
    train_new_model,
    predict_score,
    get_sentiments,
    get_entities
)
from .crawler_interface import (
    setup_webdriver,
    fetch_url,
    analyze_html
)
from .config import CFG

