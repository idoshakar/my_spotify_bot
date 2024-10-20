import tweepy

api_key = "UAZHnGBtPXsYrfaEoU22s9fLW"
api_secret = "URPY1pvPQdMFnkA2UK7fzxXctMhYlAXJOj1M1CnBFcHUfephPT"
bearer_token = "AAAAAAAAAAAAAAAAAAAAAPXrwQEAAAAA6a%2FsKoSV5XbC04jaaPkMqK0aW2U%3D6pWx5dGq7Iao692uKKXHVLh8oHxapl8Cgo1wU2pftrs0uxl8rU"
access_token = "3107542848-hZHl56nBFyejT3FteRBJggQkTXo9keZSPJn9pz7"
access_token_secret = "rY2ZM6hwOcLF83IHFiZxmWfqAWNZAZrzcjlAEX6Kv8urV"
client = tweepy.Client(bearer_token, api_key, api_secret, access_token, access_token_secret)
auth = tweepy.OAuthHandler(api_key, api_secret, access_token, access_token_secret)

def make_tweet(text):
    client.create_tweet(text=text)

if __name__ == '__main__':
    make_tweet("go to google.com")