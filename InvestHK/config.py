
class CFG:

    ####################################################################################
    #  IVHKCrawler 
    ####################################################################################
    

    CHROME_DRIVER_PATH = r"L:\ChromeDriver\108-0-5359-71\chromedriver.exe"
    CRAWLER_LOG_PATH = r'crawler.log'
    SUPPORTED_WEBSITES = [
        'bloomberg',
        'cnbc',
        'financialtimes',
        'xinhuanet',
        'reuters',
        'xinhuanet_chinese',
        'renminribao',
        'chinadaily',
        'GBAChinese',
        'GBAEnglish',
        'SouthCN',
        'AVCJ',
        'YiCai',
        'jiemian',
        'CNN',
        'Fintechnews'
    ]
    
    ####################################################################################
    #  IVHKModel  
    ####################################################################################
    
    # Default trainning args
    
    NUM_K_FOLDS = 5
    LEARNING_RATE = 3e-5
    NUM_EPOCHS = 5
    TRAIN_BATCH_SIZE = 2
    WEIGHT_DECAY = 0.01
    TARGET_METRIC = 'AUC'
    
    # Inference args
    
    INFER_BATCH_SIZE = 64
    
    