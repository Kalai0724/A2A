import requests

url = 'https://api.makcorps.com/citysearch/{cityname}/{page}/{currency}/{num_of_rooms}/{num_of_adults}/{check_in_date}/{check_out_date}'
api_key = '6965c8519a7ac9c384c1e41c'

url = url.format(
    cityname='Paris',
    page='0',
    currency='USD',
    num_of_rooms='1',
    num_of_adults='2',
    check_in_date='2026-01-20',
    check_out_date='2026-01-21'
)

url_with_api_key = f"{url}?api_key={api_key}"

response = requests.get(url_with_api_key)

# Print the response
try:
    response.raise_for_status()
    print(response.json())
except requests.exceptions.JSONDecodeError:
    print("Response is not valid JSON. Raw response:")
    print(response.text)
except requests.exceptions.HTTPError as e:
    print(f"HTTP error: {e}")
    print(response.text)
except Exception as e:
    print(f"Unexpected error: {e}")
    print(response.text)