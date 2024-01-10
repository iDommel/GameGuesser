#!/usr/bin/env python3
from fastapi import FastAPI
import requests
from pymongo import MongoClient
from urllib.parse import quote_plus
import random
top100=[10,60,70,80,240,320,340,400,440,550,570,620,730,4000,8930,49520,72850,96000,105600,107410,108600,203160,204360,218230,218620,221100,224260,227300,227940,230410,236390,238960,239140,242760,250900,251570,252490,252950,255710,261550,271590,272060,275390,289070,291550,292030,301520,304050,304930,322330,346110,359550,367520,377160,381210,386360,413150,417910,431960,433850,438100,444090,444200,466240,477160,489520,532210,550650,552990,578080,582010,632360,648800,739630,755790,814380,892970,901583,945360,990080,1046930,1063730,1085660,1086940,1089350,1091500,1097150,1172470,1174180,1203220,1222670,1238810,1240440,1245620,1468810,1517290,1599340,1811260,1938090,1966720]

app = FastAPI()

uri = 'mongodb+srv://admin:123123123123@testcluster.ggkzplp.mongodb.net/game_guesser'
client = MongoClient(uri)
db = client['game_guesser']  # Replace with your database name

@app.post("/set_current_game")
async def set_current_game(appid: int):
    result = db['games'].find_one({"appid": appid})
    if result is None:
        return {"status": "AppID not found"}
    else:
        current_game_id = result["_id"]
        db['current-game'].delete_many({})
        db['current-game'].insert_one({"appid": appid, "game_id": current_game_id})
        return {"status": f"Current game set successfully: {str(appid)}"}

@app.get("/randomize_current_game")
async def randomize_current_game():
    games = db['games'].find({})
    game_count = db['games'].count_documents({})

    if game_count == 0:
        return {"status": "No games found"}

    random_index = random.randint(0, game_count - 1)
    random_game = games[random_index]

    current_game_id = random_game["_id"]
    db['current-game'].delete_many({})
    db['current-game'].insert_one({"appid": random_game["appid"], "game_id": current_game_id})

    return {"status": f"Current game randomized successfully"}

@app.post("/check_appid")
async def check_appid(pseudo: str, appid: int):
    result = db['current-game'].find_one({"appid": appid})
    if result is None:
        return {"status": "Wrong guess"}
    else:
        return {"status": "win"}

@app.get("/fill_db")
async def fill_db():
    for appid in top100:
        url = f'https://store.steampowered.com/api/appdetails?appids={appid}'
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()

            if data[str(appid)]['success']:
                game_name = data[str(appid)]['data']['name']
                game_developers = data[str(appid)]['data']['developers']
                game_publishers = data[str(appid)]['data']['publishers']
                if data[str(appid)]['data']['is_free'] is True:
                    game_price = "Free"
                elif data.get(str(appid), {}).get('data', {}).get('price_overview', {}).get('final_formatted') is not None:
                    game_price = data[str(appid)]['data']['price_overview']['final_formatted']
                else:
                    game_price = "Free"
                if data.get(str(appid), {}).get('data', {}).get('metacritic', {}).get('score') is not None:
                    game_score = data[str(appid)]['data']['metacritic']['score']
                game_categories = []
                if data.get(str(appid), {}).get('data', {}).get('categories') is not None:
                    for category in data[str(appid)]['data']['categories']:
                        category_description = category.get('description')
                        if category_description is not None:
                            game_categories.append(category_description)
                game_genre = data[str(appid)]['data']['genres'][0]['description']
                game_release = data[str(appid)]['data']['release_date']['date']
                game_required_age = data[str(appid)]['data']['required_age']

                result = db.games.insert_one({"appid": appid, "name": game_name, "developers": game_developers, "publishers": game_publishers, "price": game_price, "score": game_score, "categories": game_categories, "genre": game_genre, "release": game_release, "required_age": game_required_age})
            else:
                print(f"AppID: {appid}, Erreur lors de la récupération des données.")
        else:
            print(f"AppID: {appid}, Erreur lors de la requête API. Code de statut: {response.status_code}")


    return {"status": "Data fetched and stored successfully"}
