
import requests

#  client_id = '3u7k9lr3aft40ndd5ktx9yjtath0gq'
#  secret_key = 'e7h8nmq7sgpag2s6tzz4qv1dpocn7u'
#  token = 'nehxuzkdt9hopkw7frz59hn72gq7ti'
#  streamer_name = 'nonifow'
#  user_id = 'gecdada70b25dfc2x52p5voe2s9t9x'


client_id = '3u7k9lr3aft40ndd5ktx9yjtath0gq'
client_secret = 'e7h8nmq7sgpag2s6tzz4qv1dpocn7u'
streamer_name = 'nonifow'

def check_stream():
    body = {
        'client_id': client_id,
        'client_secret': client_secret,
        "grant_type": 'client_credentials'
    }
    response = requests.post('https://id.twitch.tv/oauth2/token', body)

    keys = response.json()
    headers = {
        'Client-ID': client_id,
        'Authorization': 'Bearer ' + keys['access_token']
    }
    stream = requests.get('https://api.twitch.tv/helix/streams?user_login=' + streamer_name, headers=headers)
    stream_data = stream.json()


    if len(stream_data['data']) == 1:
        print(f'{streamer_name} -- Стрим запущен.')
        return True
    
    else:
        return False

if __name__ == '__main__':
    check_stream()