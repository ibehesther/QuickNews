from flask import Flask, render_template
import requests

app = Flask(__name__)

BASE_URL = "https://hacker-news.firebaseio.com/v0"

url = BASE_URL+"/item/32877585/.json"



def getFirst100RecentNews():
    top100RecentNews= []
    newstories_url = BASE_URL+'/topstories.json?orderBy="$priority"&limitToFirst=10'
    newstories_response = requests.get(url=newstories_url).json()
    for item in newstories_response:
        url = BASE_URL+"/item/"+str(item)+"/.json"
        response = requests.get(url=url).json()
        top100RecentNews.append(response)
    return top100RecentNews

@app.route('/')
def index():
    return render_template("index.html", stories= getFirst100RecentNews())


if(__name__ == "__main__"):
    app.debug = True
    app.run(host= "127.0.0.1", port= 8000)
