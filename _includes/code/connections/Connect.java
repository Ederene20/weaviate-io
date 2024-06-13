// THIS FILE HASN'T BEEN TESTED TO RUN END-TO-END

// START APIKeyWCD
// Set these environment variables
// WEAVIATE_URL      your WCD instance URL
// WEAVIATE_API_KEY  your WCD instance API key

package your.application;

import io.weaviate.client.Config;
import io.weaviate.client.WeaviateClient;
import io.weaviate.client.WeaviateAuthClient;

public class Cloud
{
    public static void main( String[] args )  throws Exception
    {

    String scheme = "https";
    String host = System.getenv("WEAVIATE_URL");
    String apiKey = System.getenv("WEAVIATE_API_KEY");

    Config config = new Config(scheme, host);
    WeaviateClient client = WeaviateAuthClient.apiKey(config, apiKey);
    }
}
// END APIKeyWCD

// START ThirdPartyAPIKeys
// Set these environment variables
// WEAVIATE_URL      your WCD instance URL
// WEAVIATE_API_KEY  your WCD instance API key
// COHERE_API_KEY    your Cohere API key

package your.application;

import java.util.HashMap;
import java.util.Map;
import io.weaviate.client.Config;
import io.weaviate.client.WeaviateClient;
import io.weaviate.client.WeaviateAuthClient;

public class ThirdParty
{
    public static void main( String[] args )  throws Exception
    {

    String scheme = "https";
    String host = System.getenv("WEAVIATE_URL");
    String apiKey = System.getenv("WEAVIATE_API_KEY");
    String cohereKey = System.getenv("COHERE_API_KEY");

    Map<String, String> headers = new HashMap<String, String>() { {
        put("X-Cohere-Api-Key", cohereKey);
    } };

    Config config = new Config(scheme, host, headers);
    WeaviateClient client = WeaviateAuthClient.apiKey(config, apiKey);
    }
}
// END ThirdPartyAPIKeys