import base64

def deshifrate():
    with open("TOKEN.tef", "r") as file: 
        token = file.readline()
        token = base64.b16decode(token)
        token = base64.b32decode(token)
        token = base64.b64decode(token)
        token = base64.a85decode(token)

    decoded_token = token.decode()
    return decoded_token