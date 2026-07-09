import requests

#request 1
url = "https://wits.worldbank.org/API/V1/wits/datasource/trn/country/840"

response = requests.get(url)

print(response.status_code)
#print(response.text[:500])

#request 2

url = (
    "https://wits.worldbank.org/API/V1/SDMX/V21/"
    "datasource/TRN/"
    "reporter/840/"
    "partner/000/"
    "product/020110/"
    "year/2000/"
    "datatype/reported"
    "?format=JSON"
)

response = requests.get(url)

print(response.status_code)
#print(response.headers["Content-Type"])
#print(response.text[:500])


data = response.json()

print(type(data))
print(data.keys())


#helper functions