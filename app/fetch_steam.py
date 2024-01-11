#!/usr/bin/env python3
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import requests
from pymongo import MongoClient
from urllib.parse import quote_plus
import random
import json
top100=[10,60,70,80,240,320,340,400,440,550,570,620,730,4000,8930,49520,72850,96000,105600,107410,108600,203160,204360,218230,218620,221100,224260,227300,227940,230410,236390,238960,239140,242760,250900,251570,252490,252950,255710,261550,271590,272060,275390,289070,291550,292030,301520,304050,304930,322330,346110,359550,367520,377160,381210,386360,413150,417910,431960,433850,438100,444090,444200,466240,477160,489520,532210,550650,552990,578080,582010,632360,648800,739630,755790,814380,892970,901583,945360,990080,1046930,1063730,1085660,1086940,1089350,1091500,1097150,1172470,1174180,1203220,1222670,1238810,1240440,1245620,1468810,1517290,1599340,1811260,1938090,1966720]

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

uri = 'mongodb+srv://admin:123123123123@testcluster.ggkzplp.mongodb.net/game_guesser'
client = MongoClient(uri)
db = client['game_guesser']  # Replace with your database name

@app.get("/games")
def get_games():
    games_cursor = db['games'].find({}, {"_id": 0})
    games = list(games_cursor)
    game_count = db['games'].count_documents({})

    print("game_count", game_count)
    print("games", games)

    if game_count == 0:
        raise HTTPException(status_code=404, detail="No games found")
    else:
        return JSONResponse(status_code=200, content=games)

@app.get("/games/{appid}")
async def get_game(appid: int):
    result = db['games'].find_one({"appid": appid}, {"_id": 0})
    if result is None:
        return HTTPException(status_code=404, detail=f"Game not found for this AppID: {appid}")
    else:
        return JSONResponse(status_code=201, content=result)

@app.post("/set_current_game")
async def set_current_game(appid: int):
    result = db['games'].find_one({"appid": appid})
    if result is None:
        return {"status": "AppID not found"}
    else:
        db['history'].delete_many({})
        current_game_id = result["_id"]
        db['current-game'].delete_many({})
        db['current-game'].insert_one({"appid": appid, "game_id": current_game_id})
        return {"status": f"Current game set successfully: {str(appid)}"}

@app.get("/get_current_game")
async def get_current_game():
    result = db['current-game'].find_one({})
    if result is None:
        raise HTTPException(status_code=404, detail="No current game found")
    else:
        return JSONResponse(status_code=201, content=result)

@app.get("/randomize_current_game")
async def randomize_current_game():
    games = db['games'].find({})
    game_count = db['games'].count_documents({})
    db['history'].delete_many({})
    if game_count == 0:
        return {"status": "No games found"}

    random_index = random.randint(0, game_count - 1)
    random_game = games[random_index]

    current_game_id = random_game["_id"]
    db['current-game'].delete_many({})
    db['current-game'].insert_one({"appid": random_game["appid"], "game_id": current_game_id})

    return {"status": f"Current game randomized successfully"}

def initialize_history(player_name: str):
    db['history'].insert_one({"player_name": player_name,
                              "name": "",
                              "developers": [],
                              "publishers": [],
                              "price": -1,
                              "score": -1,
                              "genres": [],
                              "categories": [],
                              "release": -1})

@app.post("/guess")
async def guess(player_name: str, appid: int):
    guessed_game = db['games'].find_one({"appid": appid})
    current_game = db['current-game'].find_one({})
    correct_game = db['games'].find_one({"appid": current_game["appid"]})
    result = db['current-game'].find_one({"appid": appid})
    if guessed_game is None:
        return {"status": "AppID not found"}
    if result is None:

        print("guessed_game name", guessed_game["name"])
        print("correct_game name", correct_game["name"])
        currentHistory = db['history'].find_one({"player_name": player_name})


        if currentHistory is None:
            initialize_history(player_name)
            currentHistory = db['history'].find_one({"player_name": player_name})

        name = currentHistory["name"]
        developers = currentHistory["developers"]
        publishers = currentHistory["publishers"]
        price = currentHistory["price"]
        score = currentHistory["score"]
        genres = currentHistory["genres"]
        categories = currentHistory["categories"]
        release = currentHistory["release"]


        if currentHistory["name"] == "" and guessed_game["name"] == correct_game["name"]:
                name = guessed_game["name"]
        if currentHistory["developers"] == []:
            for developer in guessed_game["developers"]:
                if developer in correct_game["developers"]:
                    developers.append(developer)
        if currentHistory["publishers"] == []:
            for publisher in guessed_game["publishers"]:
                if publisher in correct_game["publishers"]:
                    publishers.append(publisher)
        if currentHistory["price"] == -1 and guessed_game["price"] == correct_game["price"]:
            price = guessed_game["price"]
        if currentHistory["score"] == -1 and guessed_game["score"] == correct_game["score"]:
            score = guessed_game["score"]
        if currentHistory["genres"] == []:
            for i in guessed_game["genres"]:
                if i in correct_game["genres"]:
                    genres.append(i)
        if currentHistory["categories"] == []:
            for category in guessed_game["categories"]:
                if category in correct_game["categories"]:
                    categories.append(category)
        if currentHistory["release"] == -1 and guessed_game["release"] == correct_game["release"]:
            release = guessed_game["release"]
        db['history'].find_one_and_replace({"player_name": player_name}, {"player_name": player_name, "name": name, "developers": developers, "publishers": publishers, "price": price, "score": score, "genres": genres, "categories": categories, "release": release})
        currentHistory = db['history'].find_one({"player_name": player_name}, {"_id": 0})

        return JSONResponse(status_code=201, content=currentHistory)
    else:
        return JSONResponse(status_code=201, content={"status": "Correct guess ! You win !"})

def serialize_game_data(appid, data):
    game_data = data[str(appid)]['data']

    # Ensure developers and publishers are lists
    developers = game_data.get('developers', [])
    publishers = game_data.get('publishers', [])

    # Categories and Genres should also be lists
    categories = [category.get('description') for category in game_data.get('categories', []) if category.get('description')]
    genres = [genre.get('description') for genre in game_data.get('genres', []) if genre.get('description')]

    serialized_data = {
        "appid": appid,
        "name": game_data.get('name', ''),
        "developers": developers if isinstance(developers, list) else list(developers),
        "publishers": publishers if isinstance(publishers, list) else list(publishers),
        "price": game_data.get('price_overview', {}).get('final_formatted', 'Free'),
        "score": game_data.get('metacritic', {}).get('score', None),
        "categories": categories,
        "genres": genres,
        "release": game_data.get('release_date', {}).get('date', ''),
        "required_age": game_data.get('required_age', '')
    }
    return serialized_data

def update_companies(companies):
    for company in companies:
        if not db.companies.find_one({"name": company}):
            db.companies.insert_one({"name": company})

@app.get("/fill_db")
async def fill_db():
    for appid in top100:
        url = f'https://store.steampowered.com/api/appdetails?appids={appid}'
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()

            if data[str(appid)]['success']:
                game_data = serialize_game_data(appid, data)
                print(game_data)
                # Update companies collection
                update_companies(game_data['developers'] + game_data['publishers'])

                # Insert game data into the games collection
                db.games.insert_one(game_data)
            else:
                raise HTTPException(status_code=400, detail={f"AppID: {appid}, Error in data retrieval."})
        else:
            raise HTTPException(status_code=400, detail={f"AppID: {appid}. API request error, check if appid is valid."})

    return {"status": "Data fetched and stored successfully"}

@app.get("/fill_db_user")
async def fill_db_user(steamid: int):
    url_games = f'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key=EFEC8A77131A5A757FE30442C93005E1&steamid={steamid}&format=json'
    url_user = f'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=EFEC8A77131A5A757FE30442C93005E1&steamids={steamid}'
    response_games = requests.get(url_games)
    response_user = requests.get(url_user)

    if response_user.status_code == 200:
        data = response_user.json()
        steamid = data['response']['players'][0]['steamid']
        player_name = data['response']['players'][0]['personaname']
        profile_url = data['response']['players'][0]['profileurl']
        avatar = data['response']['players'][0]['avatarfull']
        country = data['response']['players'][0]['loccountrycode']

    if response_games.status_code == 200:
        data = response_games.json()
        games_count = data['response']['game_count']
        games_list = []
        for game in data['response']['games']:
            appid = game['appid']
            playtime_forever = game['playtime_forever']
            url_user_game = f'http://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/?appid={appid}&key=EFEC8A77131A5A757FE30442C93005E1&steamid={steamid}'
            response_user_game = requests.get(url_user_game)
            if response_user_game.status_code == 200:
                data = response_user_game.json()
                achievements_list = []
                if data['playerstats']['success'] is True:
                    for achievement in data['playerstats']['achievements']:
                        apiname = achievement['apiname']
                        achieved = achievement['achieved']
                        unlocktime = achievement['unlocktime']
                        achievements_list.append({"apiname": apiname, "achieved": achieved, "unlocktime": unlocktime})
                games_list.append({"appid": appid, "playtime_forever": playtime_forever, "steamid": steamid, "achievements_list": achievements_list})
            print(f"{playtime_forever}")

        result_user = db.user.insert_one({"steamid": steamid, "name": player_name, "profileUrl": profile_url, "avatar": avatar, "country": country, "game_count": games_count})
        result_user_games = db["user-games"].insert_one({"game_list": games_list})
    return {"status": "Data fetched and stored successfully"}
