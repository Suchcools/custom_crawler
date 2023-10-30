import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from pydork.engine import SearchEngine

# SearchEngine
search_engine = SearchEngine()

search_engine.set('baidu')
search_result = search_engine.search('怎么回事')
print(search_result)