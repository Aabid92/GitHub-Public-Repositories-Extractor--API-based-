import requests
from pymongo import MongoClient, errors


def fetch_github_repos(username):

    url = f"https://api.github.com/users/{username}/repos"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # raises HTTPError for 4xx/5xx
        return response.json()
    
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
    except requests.exceptions.HTTPError as http_err:
        print(f"❌ HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as err:
        print(f"❌ Request error: {err}")
    
    return None


def store_in_mongodb(repos):
    try:
        client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=5000)
        db = client["github_data"]
        collection = db["repositories"]

        for repo in repos:
            data = {
                "repo_id": repo.get("id"),  # UNIQUE
                "name": repo.get("name"),
                "stars": repo.get("stargazers_count"),
                "language": repo.get("language"),
                "url": repo.get("html_url")
            }

            collection.update_one(
                {"repo_id": data["repo_id"]},   # match condition
                {"$set": data},                 # update data
                upsert=True                     # insert if not exists
            )

        print("✅ Data stored/updated without duplicates")

    except errors.PyMongoError as err:
        print(f"❌ MongoDB error: {err}")



if __name__ == "__main__":
    username = input("Enter GitHub username: ").strip()

    if not username:
        print("❌ Username cannot be empty")
    else:
        repos = fetch_github_repos(username)
        if repos:
            store_in_mongodb(repos)
        else:
            print("❌ No data to store")
