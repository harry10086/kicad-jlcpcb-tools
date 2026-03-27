import sys
import os

# add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from lcsc_api import LCSC_API

api = LCSC_API()
res = api.search_szlcsc("10k 0603")
print("Success:", res.get("success"))
print("Msg:", res.get("msg"))
print("Total:", res.get("total"))
print("Results:", len(res.get("results", [])))
if res.get("results"):
    print("First result:", res["results"][0])
