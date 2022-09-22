# Challenge
------------------

## Have you ever heard of Hacker News? It's a great source of tech-related news. They provide a public API at https://hackernews.api-docs.io.

### The goal is to make a web app to make it easier to navigate the news:

Choose a web framework of your choice. Django, Flask, use what you like. Make a new virtualenv and pip install it;
Make a scheduled job to sync the published news to a DB every 5 minutes. You can start with the latest 100 items, and sync every new item from there. Note: here are several types of news (items), with relations between them;
Implement a view to list the latest news;
Allow filtering by the type of item;
Implement a search box for filtering by text;
As there are hundreds of news you probably want to use pagination or lazy loading when you display them.
It is also important to expose an API so that our data can be consumed:

- GET : List the items, allowing filters to be specified;
- POST : Add new items to the database (not present in Hacker News);

Bonus

- Only display top-level items in the list, and display their children (comments, for example) on a detail page;
- In the API, allow updating and deleting items if they were created in the API (but never data that was retrieved from Hacker News);
- Be creative! :)

### To get project started
- Create virtual environment
    - For windows/Linux/Mac:
        `py -3 -m venv name_of_your_venv`
- Activate virtual environment
    - For windows:
        `name_of_venv\Scripts\activate`
    - For Linux/Mac:
        ```
        source
        name_of_venv/bin/activate
        ```
- Install all the required packages
   ` pip install -r requirements.txt `
- Start the server
    ` py app.py `

Application should be up and running on `http:127.0.0.1:8000`