from flask import Flask, render_template, request, jsonify, abort
from flask_cors import CORS
import requests
from models import db, setup_db, News

app = Flask(__name__)
cors = CORS(app, resources={r"/api/v1.0/*": {"origins": "*"}});

setup_db(app)
BASE_URL = "https://hacker-news.firebaseio.com/v0"



def getFirst100RecentNews():
    top100RecentNews= []
    newstories_url = BASE_URL+'/topstories.json?orderBy="$priority"&limitToFirst=100'
    newstories_response = requests.get(url=newstories_url).json()
    for item in newstories_response:
        url = BASE_URL+"/item/"+str(item)+"/.json"
        response = requests.get(url=url).json()
        top100RecentNews.append(response)
    return top100RecentNews

# Get all news
@app.route("/api/v1.0/news")
def getNews():
    body = []
    page = request.args["page"]
    NEWS_PER_PAGE = 10
    start = (int(page) - 1) * NEWS_PER_PAGE
    end = start + NEWS_PER_PAGE
    
    try:
        news = News.query.order_by(db.desc(News.time)).all()
        for item in news:
            news_details = {
                "id": item.id,
                "type": item.type,
                "author": item.author,
                "source": item.source,
                "time": item.time,
                "title": item.title,
                "url": item.url,
                "comments": item.comments
            }
            body.append(news_details)
        body = body[start: end]
    except Exception:
        abort(404)
    return jsonify({"response": body})

# Filter news by on type
@app.route("/api/v1.0/news/<string:news_type>")
def getNewsByType(news_type):
    body = []
    page = request.args["page"]
    NEWS_PER_PAGE = 10
    start = (int(page) - 1) * NEWS_PER_PAGE
    end = start + NEWS_PER_PAGE
    
    try:
        news = News.query.filter(News.type == news_type).order_by(db.desc(News.time)).all()
        for item in news:
            news_details = {
                "id": item.id,
                "type": item.type,
                "author": item.author,
                "source": item.source,
                "time": item.time,
                "title": item.title,
                "url": item.url,
                "comments": item.comments
            }
            body.append(news_details)
        body = body[start: end]
    except Exception:
        abort(404)
    return jsonify({"response": body})

# Filter news by search term
@app.route("/api/v1.0/news/search", methods=["POST"])
def getNewsBySearchTerm():
    body = []
    search_term = request.get_json()['search_term']
    
    try:
        news = News.query.filter(News.title.ilike('%'+search_term+'%')).all()
        for item in news:
            news_details = {
                "id": item.id,
                "type": item.type,
                "author": item.author,
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

# Create news
@app.route("/api/v1.0/news", methods=["POST"])
def add_news():
    body = {}
    try:
        request = request.get_json()
        type = request.get("type")
        author = request.get("author")
        time = request.get("time", 0)
        title = request.get("title", "")
        url = request.get("url", "")
        comments = request.get("comments", [])
        if(type):
            news = News(type=type, source="user", time=time, author=author,
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

# Route to populate database with first 100 news from Hacker News API
@app.route("/api/v1.0/hn_news", methods=["POST"])
def add_hn_news():
    all_news = []
    first100News = getFirst100RecentNews()
    # Get news details needed 
    for item in first100News:
        type = item["type"]
        # set default value for optional field in Hacker News API
        author = item.setdefault("by", "Anon")
        title = item.setdefault("title", "No title")
        time = item.setdefault("time", 0)
        url= item.setdefault('url', "https://google.com")
        comments = item.setdefault("kids", [])
        news = {
            "type": type,
            "author": author,
            "title": title,
            "source": "HN_API",
            "time": time,
            "url": url,
            "comments": comments
        }
        all_news.append(news)
    
    # Add news to database
    for news in all_news:
        type = news["type"]
        author = news["author"]
        source = news["source"]
        title = news["title"]
        time = news["time"]
        url= news["url"]
        comments = news["comments"]
        try:
            new_news = News(type=type, source=source, time=time, 
                        author=author, title=title, url=url, comments=comments)
            db.session.add(new_news)
            db.session.commit()
        except Exception:
            db.session.rollback()
            abort(400)
        finally:
            db.session.close()
    return jsonify(all_news)

@app.route('/')
def index():
    url = "http://127.0.0.1:8000/api/v1.0/news?page=1"
    news = requests.get(url=url).json()
    return render_template("index.html", stories=news["response"])

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
