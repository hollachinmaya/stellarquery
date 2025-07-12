import requests

def query_gaia(adql: str):
    """
    Query the ESA Gaia Archive TAP+ service with a validated ADQL string.
    """
    url = "https://gea.esac.esa.int/tap-server/tap/sync"
    params = {
        "REQUEST": "doQuery",
        "LANG": "ADQL",
        "FORMAT": "json",
        "QUERY": adql
    }

    resp = requests.get(url, params=params)
    
    print(f"🌐 Gaia TAP+ response: {resp.status_code}")
    if resp.status_code == 200:
        try:
            return resp.json()  # Return the data as JSON
        except Exception as e:
            raise Exception("Gaia API response is not valid JSON")
    else:
        raise Exception(f"Gaia API error {resp.status_code}: {resp.text}")
