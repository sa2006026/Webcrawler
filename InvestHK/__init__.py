from .model_interface import (
    train_new_model,
    predict_score,
    get_sentiments,
    get_entities,
    translate_en_to_zh,
    translate_hk_to_en,
    translate_hk_to_zh,
)
from .crawler_interface import (
    setup_webdriver,
    fetch_url,
    analyze_html
)
from .config import CFG

