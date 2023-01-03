from .AnalyzeHTML import *
from .FetchURL import *
from .Utils import *


analyze_funcs = [func for func in dir(AnalyzeHTML) if func.startswith('analyze')]
analyze_types = [func.split('_')[1] for func in analyze_funcs]
type2funcs = {}
for t in set(analyze_types):
    type2funcs[t] = [func for func in analyze_funcs if func.split('_')[1] == t]

def get_analyze_funcs(website):
    return type2funcs[website]
    