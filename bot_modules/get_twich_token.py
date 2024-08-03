import requests

client_id = '3u7k9lr3aft40ndd5ktx9yjtath0gq'
secret_key = 'e7h8nmq7sgpag2s6tzz4qv1dpocn7u'
token = 'nehxuzkdt9hopkw7frz59hn72gq7ti'

response = requests.post(
    'https://id.twitch.tv/oauth2/token',
    data={
        'client_id': '3u7k9lr3aft40ndd5ktx9yjtath0gq',
        'client_secret': 'e7h8nmq7sgpag2s6tzz4qv1dpocn7u',
        'grant_type': 'client_credentials'
    }
)
if response.status_code == 200:
    response_json = response.json()
    print(response_json['access_token'])