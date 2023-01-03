import datetime

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from .config import CFG
from .IVHKCrawler import FetchURL, AnalyzeHTML, get_analyze_funcs


def setup_webdriver(headless: bool = False, pictures: bool = True, scripts: bool = True):
    """
    Create a chrome webdriver instance with selenium.
    Should have chrome driver excutable in config.py -> CHROME_DRIVER_PATH

    Parameters
    ----------
    headless : bool (Default to False)
        Whether the driver is created without a window.
        headless=False means a window will be create.
        Some anti-crawler methods will detect this if set to True.
    
    picture : bool (Default to False)
        Whether the driver receives pictures from website.
    
    scripts : bool (Default to False)
        Whether the driver receives js scripts from website.

    Returns
    -------
    selenium.webdriver.chrome.webdriver.WebDriver
        The website driver Instance.
    """
    chrome_options = Options()
    chrome_prefs = {}

    if not pictures:
        chrome_prefs["profile.managed_default_content_settings.images"] = 2
    if not scripts:
        chrome_prefs["profile.managed_default_content_settings.javascript"] = 2

    chrome_options.add_experimental_option("prefs", chrome_prefs)

    if headless:
        chrome_options.add_argument("--headless") # Hides the browser window
    # Reference the local Chromedriver instance
    # chrome_options.add_argument('--proxy-server=http://127.0.0.1:9910')
    driver = webdriver.Chrome(executable_path=CFG.CHROME_DRIVER_PATH, options=chrome_options)
    return driver


def fetch_url(driver: webdriver.chrome.webdriver.WebDriver, website: str, query: str, \
            from_date: datetime.datetime, to_date: datetime.datetime):
    """
    Fetch news from given website by search with given query.
    Return results published during from date_from to date_to.

    Parameters
    ----------
    driver : selenium.webdriver.chrome.webdriver.WebDriver
        Selenium webdriver to use.
    
    website : str
        Website to fetch news from.
        For supported websites list Please check InvestHK.CFG.SUPPORTED_WEBSITES
    
    query : str
        Query string to search with on news sites.
    
    date_from : datetime.datetime
        When the query time range starts.
    
    date_to : datetime.datetime
        When the query time range ends.

    Returns
    -------
    List of query results.

    Sample Output
    -------
    [News0, News1, News2, ..]
    
    Each News is a python Dict:\n
    {
        'title': 'Example news title.',
        'url': 'https://example.com',
        'datetime': datetime.datetime(2022, 11, 29, 0, 0),
    }

    """
    if website not in CFG.SUPPORTED_WEBSITES:
        raise NotImplementedError(f"Website not supported, supported websites are: {CFG.SUPPORTED_WEBSITES}")
    
    func = getattr(FetchURL, 'fetch_url_from_' + website)
    
    return func(driver, query, from_date, to_date)

def analyze_html(html:str, website:str =None):
    """
    Analyze given html string / file,
    Return news titles & contents

    Parameters
    ----------
    html : str | _io.TextIOWrapper
        html text string  /  html file of news page
    
    website : str | None (Default to None)
        Website the news page is fetched from.
        If set to None, each matching pattern will be tried in turn.
        For supported websites list Please check InvestHK.SUPPORTED_WEBSITES.

    Returns
    -------
    Tuple of Two lists: list of news titles & list of news contents

    Sample Output
    -------
    (['title0', 'title1', 'title2', ..], ['content0', 'content1', 'content2', ..])

    P.S. In most cases, an html file contains only a title and a content, but there are exceptions

    """
    
    if website is not None and website not in CFG.SUPPORTED_WEBSITES:
        raise NotImplementedError(f"Website not supported, supported websites are: {CFG.SUPPORTED_WEBSITES}")
    
    if website is not None:
        analyze_func_names = get_analyze_funcs(website)
    else:
        analyze_func_names = []
        for site in CFG.SUPPORTED_WEBSITES:
            analyze_func_names += get_analyze_funcs(site)
            
    titles, contents = [], []
    
    
    if type(html) == str:
        with open(html, encoding='utf-8') as f:
            soup = BeautifulSoup(f, features="lxml")
    else:
        soup = BeautifulSoup(html, features="lxml")

    for funcc_name in analyze_func_names:
        analyze_func = getattr(AnalyzeHTML, funcc_name)
        titles, contents = analyze_func(soup)
        if not (titles == [] or contents == []):
            break

    return titles, contents


