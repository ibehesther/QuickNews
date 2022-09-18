from flask import Flask, render_template, request, jsonify, abort
import requests
from models import db, setup_db, News

app = Flask(__name__)

setup_db(app)
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

@app.route("/news")
def getNews():
    body = []
    try:
        news = News.query.all()
        for item in news:
            news_details = {
                "id": item.id,
                "type": item.type,
                "source": item.source,
                "time": item.time,
                "title": item.title,
                "url": item.url,
                "comments": item.comments
            }
            body.append(news_details)
    except Exception:
        abort(404)
    return jsonify({"response": body})

@app.route("/news", methods=["POST"])
def add_news():
    body = {}
    try:
        request = request.get_json()
        type = request.get("type")
        source = request.get("source")
        time = request.get("time", 0)
        title = request.get("title", "")
        url = request.get("url", "")
        comments = request.get("comments", [])
        if(type and source):
            news = News(type=type, source=source, time=time, 
                        title=title, url=url, comments=comments)
            db.session.add(news)
            body["type"] = news.type
            body["source"] = news.source
            body["time"] = news.time
            body["title"] = news.title
            body["url"] = news.url
            body["comments"] = news.comments
            db.session.commit()
        else:
            abort(400)
    except Exception:
        db.session.rollback()
        abort(400)
    finally:
        db.session.close()
    return jsonify({"response": body})

@app.route('/')
def index():
    return render_template("index.html", stories= getFirst100RecentNews())

# Error handlers
@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        'success': False,
        'error': 400,
        'message': 'Bad Request'
    }), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': 'Not Found'
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'success': False,
        'error': 405,
        'message': 'Method Not Allowed'
    }), 405


if(__name__ == "__main__"):
    app.debug = True
    app.run(host= "127.0.0.1", port= 8000)
