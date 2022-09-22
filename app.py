from sqlite3 import Date
from flask import Flask, render_template, request, jsonify, abort
from flask_cors import CORS
import requests
from datetime import datetime
from models import db, setup_db, News, Comments

app = Flask(__name__)
cors = CORS(app, resources={r"/api/v1.0/*": {"origins": "*"}});

setup_db(app)
BASE_URL = "https://hacker-news.firebaseio.com/v0"


def getNewsItem(item):
    url = BASE_URL+"/item/"+str(item)+"/.json"
    response = requests.get(url=url).json()
    return response

def getRecentNews(number):
    topRecentNews= []
    newstories_url = BASE_URL+'/newstories.json?orderBy="$priority"&limitToFirst='+str(number)
    newstories_response = requests.get(url=newstories_url).json()
    for item in newstories_response:
        response = getNewsItem(item)
        topRecentNews.append(response)
    return topRecentNews

def getMostRecentNews(lastNewsKey):
    mostRecentNews= []
    newstories_url = BASE_URL+'/newstories.json'
    newstories_response = requests.get(url=newstories_url).json()
    for item in newstories_response:
        if(item > int(lastNewsKey)):
            url = BASE_URL+"/item/"+str(item)+"/.json"
            response = requests.get(url=url).json()
            mostRecentNews.append(response)
        else:
            break
    return mostRecentNews

@app.after_request
def after_request(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add(
        "Access-Control-Allow-Methods", "GET, POST, DELETE, PATCH")
    response.headers.add("Access-Control-Allow-Headers", 'Content-Type')
    return response

# Get all news paginated
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
            comments = Comments.query.filter(Comments.news_id == item.id).all()
            comments_list = []
            for comment in comments:
                new_comment = {
                    "id": comment.id,
                    "key": comment.key,
                    "news_id": comment.news_id,
                    "text": comment.text,
                    "time": comment.time
                }
                comments_list.append(new_comment)
            news_details = {
                "id": item.id,
                "key": item.key,
                "type": item.type,
                "author": item.author,
                "source": item.source,
                "time": item.time,
                "title": item.title,
                "url": item.url,
                "comments": comments_list
            }
            body.append(news_details)
        body = body[start: end]
    except Exception:
        abort(404)
    return jsonify(body)

# Get all comments paginated
@app.route("/api/v1.0/comments")
def getComments():
    body = []
    page = request.args["page"]
    COMMENTS_PER_PAGE = 10
    start = (int(page) - 1) * COMMENTS_PER_PAGE
    end = start + COMMENTS_PER_PAGE
    try:
        comments = Comments.query.order_by(db.desc(Comments.time)).all()
        for item in comments:
            news_details = {
                "id": item.id,
                "key": item.key,
                "time": item.time,
                "text": item.text,
                "news_id": item.news_id
            }
            body.append(news_details)
        body = body[start: end]
    except Exception:
        abort(404)
    return jsonify(body)


# render template for all news 
@app.route("/news")
def returnNews():
    news = getNews().get_json()
    return render_template("all-news.html", items=news)

# render news item
@app.route('/news/<int:item_id>')
def renderNewsItem(item_id):
    news = News.query.get(item_id)
    print(news)
    return render_template("news-item.html", item=news)

# Add most recent news based on last index in database
@app.route("/api/v1.0/news/most_recent", methods=["POST"])
def addMostRecentNews():
    all_news=[]
    lastNewsId= request.args["last_news_key"]
    response = getMostRecentNews(lastNewsId)
    # Get news details needed 
    for item in response:
        type = item["type"]
        key=item["id"]
        # set default value for optional field in Hacker News API
        author = item.setdefault("by", "Anon")
        title = item.setdefault("title", "No title")
        time = item.setdefault("time", 0)
        url= item.setdefault('url', "https://google.com")
        comments = item.setdefault("kids", [])
        comments_list=[]
        if(len(comments)):
            for comment in comments:
                # set default value for optional comment field in Hacker News API
                items = getNewsItem(comment)
                text = items.setdefault("text", "")
                time = items.setdefault("time", 0)
                comment_details ={
                    "key": items["id"],
                    "time": time,
                    "text": text
                }
                comments_list.append(comment_details)
        news = {
            "key": key,
            "type": type,
            "author": author,
            "title": title,
            "source": "HN_API",
            "time": time,
            "url": url,
            "comments": comments_list
        }
        all_news.append(news)
    # Add news to database
    for news in all_news:
        key = news["key"]
        type = news["type"]
        author = news["author"]
        source = news["source"]
        title = news["title"]
        time = news["time"]
        url= news["url"]
        comments = news["comments"]
        try:
            new_news = News(key=key, type=type, source=source, time=time, 
                        author=author, title=title, url=url)
            
            if(len(comments) > 0):
                for comment in comments:
                    print(comment["time"])
                    new_comment = Comments(key=comment["key"], time=comment["time"], text=comment["text"], news=new_news)
                    db.session.add(new_comment)
            db.session.add(new_news)
            db.session.commit()
        except Exception:
            db.session.rollback()
            abort(400)
        finally:
            db.session.close()
    return jsonify(all_news)


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
    return jsonify(body)

@app.route("/news/<string:news_type>")
def renderNewsByType(news_type):
    news= getNewsByType(news_type).get_json()
    return render_template("all-news.html", items=news)


# Filter news by search term
@app.route("/api/v1.0/news/search", methods=["POST"])
def getNewsBySearchTerm():
    body = []
    # search_term = request.get_json()['search_term']
    search_term = request.form["search_term"]
    
    try:
        news = News.query.filter(News.title.ilike('%'+search_term+'%')).all()
        for item in news:
            comments = Comments.query.filter(Comments.news_id == item.id).all()
            comments_list = []
            for comment in comments:
                new_comment = {
                    "id": comment.id,
                    "key": comment.key,
                    "news_id": comment.news_id,
                    "text": comment.text,
                    "time": comment.time
                }
                comments_list.append(new_comment)
            news_details = {
                "id": item.id,
                "type": item.type,
                "author": item.author,
                "source": item.source,
                "time": item.time,
                "title": item.title,
                "url": item.url,
                "comments": comments_list
            }
            body.append(news_details)
    except Exception:
        abort(404)
    return jsonify(body)

@app.route("/news/search", methods=["POST"])
def renderNewsBySearchTerm():
    news = getNewsBySearchTerm().get_json()
    return render_template("all-news.html", items=news)

# Create news
@app.route("/api/v1.0/news", methods=["POST"])
def add_news():
    body = {}
    date = datetime.utcnow() - datetime(1970, 1, 1)
    date_in_s = round(date.total_seconds())
    try:
        req = request.get_json()
        type = req.get("type")
        author = req.get("author")
        time = int(date_in_s)
        title = req.get("title")
        url = req.get("url")
        if(type):
            news = News(type=type, source="user", time=time, author=author,
                        title=title, url=url)
            db.session.add(news)
            body["type"] = news.type
            body["source"] = news.source
            body["time"] = news.time
            body["title"] = news.title
            body["url"] = news.url
            db.session.commit()
        else:
            abort(400)
    except Exception:
        db.session.rollback()
        abort(400)
    finally:
        db.session.close()
    return jsonify(body)

# Create comments
@app.route("/api/v1.0/comments/<int:news_id>", methods=["POST"])
def add_comment(news_id):
    body = {}
    date = datetime.utcnow() - datetime(1970, 1, 1)
    date_in_s = round(date.total_seconds())
    try:
        news = News.query.get(news_id)
        if(news):
            req = request.get_json()
            time = date_in_s
            text = req.get("text", "")
            if(type):
                new_comment = Comments(time=time, text=text, news_id=news.id)
                db.session.add(new_comment)
                body["news_id"] = new_comment.news_id
                body["time"] = new_comment.time
                body["text"] = new_comment.text
                db.session.commit()
            else:
                abort(400)
    except Exception:
        db.session.rollback()
        abort(400)
    finally:
        db.session.close()
    return jsonify(body)

# Route to populate database from Hacker News API
@app.route("/api/v1.0/hn_news", methods=["POST"])
def add_hn_news():
    all_news = []
    # first 100 News from Hacker News API
    first100News = getRecentNews(100)
    # Get news details needed 
    for item in first100News:
        type = item["type"]
        key=item["id"]
        # set default value for optional field in Hacker News API
        author = item.setdefault("by", "Anon")
        title = item.setdefault("title", "No title")
        time = item.setdefault("time", 0)
        url= item.setdefault('url', "https://google.com")
        comments = item.setdefault("kids", [])
        comments_list=[]
        if(len(comments)):
            for comment in comments:
                # set default value for optional comment field in Hacker News API
                items = getNewsItem(comment)
                text = items.setdefault("text", "")
                time = items.setdefault("time", 0)
                comment_details ={
                    "key": items["id"],
                    "time": time,
                    "text": text
                }
                comments_list.append(comment_details)
        news = {
            "key": key,
            "type": type,
            "author": author,
            "title": title,
            "source": "HN_API",
            "time": time,
            "url": url,
            "comments": comments_list
        }
        all_news.append(news)
    # Add news to database
    for news in all_news:
        key = news["key"]
        type = news["type"]
        author = news["author"]
        source = news["source"]
        title = news["title"]
        time = news["time"]
        url= news["url"]
        comments = news["comments"]
        try:
            new_news = News(key=key, type=type, source=source, time=time, 
                        author=author, title=title, url=url)
            
            if(len(comments) > 0):
                for comment in comments:
                    new_comment = Comments(key=comment["key"], time=comment["time"], text=comment["text"], news=new_news)
                    db.session.add(new_comment)
            db.session.add(new_news)
            db.session.commit()
        except Exception:
            db.session.rollback()
            abort(400)
        finally:
            db.session.close()
    return jsonify(all_news)

# Update News details
@app.route("/api/v1.0/news/<int:news_id>", methods=["PATCH"])
def updateNews(news_id):
    res_news_id=None
    valid_fields=["title", "author", "url", "type"]  #These are the only fields tat can be changed
    input_fields=[]
    try:
        req = request.get_json()
        news = News.query.get(news_id)
        res_news_id = news.id
        if(news.source == "user"):
            # Get all the valid fields 
            for field in req:
                if field in valid_fields:
                    input_fields.append(field)
            if "title" in input_fields:
                news.title = req.get("title")
            if "author" in input_fields:
                news.author = req.get("author")
            if "url" in input_fields:
                news.url = req.get("url")
            if "type" in input_fields:
                news.type = req.get("type")
            db.session.commit()
        else:
            abort(400)
    except Exception():
        db.session.rollback()
        abort(404)
    finally:
        db.session.close()
    return jsonify({'success': True, 'id': res_news_id})

# Delete News details
@app.route('/api/v1.0/news/<int:news_id>', methods=['DELETE'])
def delete_question(news_id):
    res_news_id = None
    try:
        news = News.query.get(news_id)
        if(news.source=="user"):
            res_news_id = news.id
            db.session.delete(news)
            db.session.commit()
    except Exception:
        db.session.rollback()
        abort(404)
    finally:
        db.session.close()

    return jsonify({'success': True, 'id': res_news_id})

@app.route('/')
def index():
    return render_template("index.html")

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

@app.errorhandler(500)
def method_not_allowed(error):
    return jsonify({
        'success': False,
        'error': 500,
        'message': 'Internal Server Error'
    }), 500


if(__name__ == "__main__"):
    app.debug = True
    app.run(host= "127.0.0.1", port= 8000)
