const all_button = document.querySelector("#all-btn");
const story_button = document.querySelector("#story-btn");
const job_button = document.querySelector("#job-btn");
const tabs = document.querySelectorAll(".tabs>button");
const news_section = document.querySelector(".news-container");
const search_section = document.querySelector(".search-container");
const search_form = document.querySelector("#search");
const search_term = document.querySelector("#search-term");


const BASE_API_URL = "http://127.0.0.1:8000"

const getAllNews = async () => {
    let response = await fetch(`${BASE_API_URL}/api/v1.0/news?page=1`)
    response = response.json()
    return response
}

const getNewsByType = async(type) => {
    let response = await fetch(`${BASE_API_URL}/api/v1.0/news/${type}?page=1`)
    response = await response.json()
    return response
}
const getNewsbySearch = async(search_term) => {
    let response = await fetch(`${BASE_API_URL}/api/v1.0/news/search`,
    {
        method: "POST",
        body: JSON.stringify({
            search_term
        }),
        headers: {
            "Content-type": "application/json"
        }
    })
    response = await response.json()
    return response
}
const getMostRecentNews = async(lastNewsKey) => {
    let newstories_response = await fetch(`${BASE_API_URL}/api/v1.0/news/most_recent?last_news_key=${lastNewsKey}`,
    {
        method: "POST"
    })
    newstories_response = await newstories_response.json();
    return newstories_response
}

const createNewsItem = (title, time, author) => {
    const news_container = document.createElement("div");
    const news_card = document.createElement("div");
    news_card.className="news-card";
    // create an image and add it's source
    const news_img = document.createElement("img");
    news_img.src= "/static/images/news.jpg";
    news_img.alt="news image";
    // create a container for news details
    const news_details = document.createElement('div');
    news_details.className = "news-details";
    // create paragraph for news title
    const news_title = document.createElement("p");
    news_title.className = "news-title";
    news_title.innerText=title;
    // 
    const news_subdetails = document.createElement('div');
    news_subdetails.className = "news-subdetails";
    // create element for news time
    const news_time = document.createElement("p");
    news_time.className="news-time";
    news_time.innerHTML= "&#128337; " + time;
    // create element for news author
    const news_author = document.createElement("p");
    news_author.className="news-author";
    news_author.innerText="author: "+author;

    // Combine the elements together for correct formation
    news_subdetails.appendChild(news_time);
    news_subdetails.appendChild(news_author);

    news_details.appendChild(news_title);
    news_details.appendChild(news_subdetails);

    news_card.appendChild(news_img);
    news_card.appendChild(news_details);

    news_container.appendChild(news_card);

    return news_container;
}

const getAllNewsItems = (response) => {
    const news_container = document.createElement("div");
    for (item of response){
        news_item = createNewsItem(item.title, item.time, item.author);
        news_container.appendChild(news_item);
    }
    return news_container;
}

window.onload = () => {
    console.log("DOM content loading...")
    // Adding recent news to database using Hacker News API
    
    setInterval(() => {
        console.log("Fetching recent news...")
        getAllNews()
        .then(({response}) => {
            const lastNewsKey = response[0]["key"]
            const mostRecentNews = getMostRecentNews(lastNewsKey)
            mostRecentNews.then((response) => {
                console.log(lastNewsKey, response)
            })
            
        })
    .catch(console.log)
    }, 300000);
}
const makeActive = (e) => {
    // Remove the active class from every tab button
    for(button of tabs){
        button.classList = "tablink"
    }
    // Adds the active class to the clicked button alone
    e.target.classList += " active"
}

all_button.addEventListener("click", (e) => {
    makeActive(e)
    news_section.innerHTML="Loading..."
    getAllNews()
    .then(({response}) => {
        const news = getAllNewsItems(response);
        news_section.innerHTML= news.innerHTML;
    })
    .catch(console.log)
})
story_button.addEventListener("click", (e) => {
    makeActive(e)
    news_section.innerHTML="Loading..."
    getNewsByType("story")
    .then(({response}) => {
        const news = getAllNewsItems(response);
        news_section.innerHTML= news.innerHTML;
    })
    .catch(console.log)
})
job_button.addEventListener("click", (e) => {
    makeActive(e)
    news_section.innerHTML="Loading..."
    getNewsByType("job")
    .then(({response}) => {
        const news = getAllNewsItems(response);
        news_section.innerHTML= news.innerHTML;
    })
    .catch(console.log)
})
search_form.addEventListener("submit", (e) => {
    e.preventDefault();
    
    if(search_term.value.trim()){
        search_section.innerText = "Loading...";
        search_section.style.color="black";
        getNewsbySearch(search_term.value)
        .then(({response}) => {
            if(response.length){
                const news = getAllNewsItems(response);
                search_section.innerHTML= news.innerHTML;
                search_section.style.color="black";
            }else{
                search_section.innerText= "Nothing found! Try a different search";
                search_section.style.color="red";
            }
        })
        .catch(console.log)
    }
})
search_term.addEventListener('keydown', (e) => {
    search_section.innerHTML=""
})
