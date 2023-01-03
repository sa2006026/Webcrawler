import time
import traceback
from datetime import datetime

from ..config import CFG

def logg(infomation):
    timestamp = datetime.now().isoformat()
    call_from = traceback.extract_stack()[-2][2]
    line = f'[{timestamp}][{call_from}] {infomation}'
    
    with open(CFG.CRAWLER_LOG_PATH, 'a+') as f:
        f.write(line+'\n')
    return line

def fetch_elements_retry_wait(driver, url, by, value, retry=3, timeout=1.0):
    
    fetch_start = time.time()
    elements = []
    for re in range(retry):
        
        logg(f"Retry {re} : Fetching html from {url}")
        driver.get(url)
        wait_start = time.time()
        
        logg(f"Fetching elements by <{by}> value = \'{value}\'")
        while time.time() - wait_start <= timeout and elements == []:
            elements = driver.find_elements(by=by, value=value)

        if elements != []:
            logg(f"Fetch succeed. total time used: {time.time() - fetch_start}.")
            break
        else:
            logg("Fetch failed. Retrying...")
    
    return elements

def filter_result_df_date(result_df, from_date, to_date):
    
    result_df['datetime'] = result_df['datetime'].apply(lambda x: x.date())
    from_date, to_date = from_date.date(), to_date.date()
    
    is_too_early = result_df['datetime'] < from_date
    is_too_late = result_df['datetime'] > to_date
    is_ok = ~(is_too_early + is_too_late)
    
    result_df = result_df[is_ok]
    
    return result_df



        