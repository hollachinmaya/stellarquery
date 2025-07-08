import requests

def query_exoplanet(sql: str):
    """Query NASA's TAP service with a validated SQL string."""
    url = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"
    params = {
        "query": sql,
        "format": "json"
    }

    resp = requests.get(url, params=params)
    
    if resp.status_code == 200:
        try:
            return resp.json()  #  Just return the list
        except Exception as e:
            raise Exception("NASA API response is not valid JSON")
    else:
        raise Exception(f"NASA API error {resp.status_code}: {resp.text}")
