from flask import Flask
from flask import request
from flask import render_template
import requests
import json
import re

app = Flask(__name__)
app.debug = True

@app.route('/', methods=['GET', 'POST'])
def index():
    errors = []
    results = {}
    
    if request.method == "POST":
        # get text that the person has entered
        try:
            inputText = request.form['text']
        except:
            errors.append(
                "Please make sure to provide some valid words to search for Spotify Tracks and try again."
            )
            return render_template('index.html', errors=errors)
        if inputText:
            # text processing
            results = searchTracks(inputText)
   
    return render_template("index.html", errors=errors, results=results)

# Function which get spotify track name and URL
def spotifytrack(phrase):
    
    spotify= requests.get('https://api.spotify.com/v1/search?q='+'"'+phrase+'"'+'&type=track&offset=90&limit=1')
    wsjdata = json.loads(spotify.content)
    name = (wsjdata['tracks']['items'][0]['name'])
    url = wsjdata['tracks']['items'][0]['external_urls']['spotify']   
    
    #print phrase, '^', name, url
    return name, url

def searchTracks(inputText):

    #Initialize phrase to null value
    phrase = ''
    phraseold = ''
    results = []

    # Split input text by default space seperator, we could use nltk to perform n-gram and parts of speech tagging for advanced handling
    # processedText = inputText.lower()
    tokens = inputText.split()
            
    # loop through tokens one at a time and append it to build playlist
    for word in tokens:
    
        # If this first word in sentence, initialize both phrase and phraseold to first word of sentence
        if (phrase ==''):
            phrase = word
            phraseold = word
        else:
            #If its not a first word in sentence append it to existing phrase
            phraseold = phrase
            phrase = phrase+' '+word

        try:
            # Check if this phrase exists as a track in spotify
            spotify = requests.get('https://api.spotify.com/v1/search?q='+'"'+phrase+'"'+'&type=track&offset=90&limit=1')
            # Load spotify content to json format
            wsjdata = json.loads(spotify.content)

            # If no tracks with given phrase and if its not first word in sentence then no meaning in going further with phrase. 
            # So consider previous successful track i.e. phraseold
            if ((len((wsjdata['tracks']['items'])) == 0) and len(re.findall(r'\w+',phraseold))>1):
                # Getting name and url for previous phrase by calling function spotifytrack
                name,url = spotifytrack(phraseold)
                results.append(phraseold + "|" + name + "|" + url)
                # Re-initialise phrase to current word
                phrase = word
            # If no tracks with given phrase and if its the first word in sentence then we can stop going further  
            elif (len((wsjdata['tracks']['items'])) == 0):
                # Keep name as word and url as not available
                name = phraseold
                url = 'https://spotify.com'
    
                # Adding to html headline
                results.append(phraseold + "|" + "No Match Found" + "|" + url)
                
                # Re-initialise phrase to current word
                phrase = ''
            # If track exists in spotify going further by adding words
            else:
                phrase = phrase
            
        except:
            print phrase
            print "Exception"

    # For last phrase get track info
    try:
        name,url = spotifytrack(phrase)
        results.append(phrase + "|" + name + "|" + url)
    except:
        print "Exception"
        
    return results

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)