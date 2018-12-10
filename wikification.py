import sys, http.client, urllib.request, urllib.parse, urllib.error, json

from pprint import pprint



def get_url( domain, url ) :

  # Headers are used if you need authentication
  headers = {}

  # If you know something might fail - ALWAYS place it in a try ... except
  try:
    conn = http.client.HTTPSConnection( domain )
    conn.request("GET", url, "", headers)
    response = conn.getresponse()
    data = response.read()
    conn.close()
    return data
  except Exception as e:
    # These are standard elements in every error.
    print("[Errno {0}] {1}".format(e.errno, e.strerror))

  # Failed to get data!
  return None


# If this is included as a module, you have access to the above function
# without "running" the following piece of code.
# Usually, you place functions in a file and their tests in chunks like below.
def wikification(query):

  # This makes sure that any funny charecters (including spaces) in the query are
  # modified to a format that url's accept.
  query = urllib.parse.quote_plus( query )

  # Call our function.
  url_data = get_url( 'en.wikipedia.org', '/w/api.php?action=query&list=search&format=json&srsearch=' + query )

  # We know how our function fails - graceful exit if we have failed.
  if url_data is None :
    print( "Failed to get data ... Can not proceed." )
    # Graceful exit.
    # sys.exit()
    return

  # http.client socket returns bytes - we convert this to utf-8
  url_data = url_data.decode( "utf-8" )

  # Convert the structured json string into a python variable
  url_data = json.loads( url_data )

  # Pretty print
  # pprint( url_data )

  # Now we extract just the titles
  titles = [ i['title'] for i in url_data['query']['search'] ]
  # pprint( titles )

  # Make sure we can plug these into urls:
  url_titles = [ urllib.parse.quote_plus(i) for i in titles ]
  # pprint( url_titles )

  return titles