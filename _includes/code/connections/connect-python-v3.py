# THIS FILE HASN'T BEEN TESTED TO RUN END-TO-END

# START APIKeyWCD
import os
import weaviate

# Set these environment variables
URL = os.getenv("WCD_URL")
APIKEY = os.getenv("WCD_API_KEY")

# Create the client
client = weaviate.Client(
    url=URL,
    auth_client_secret=weaviate.auth.AuthApiKey(api_key=APIKEY),
)
# END APIKeyWCD
client.close()