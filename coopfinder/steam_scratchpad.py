from os import environ, path
from time import sleep
from random import randint

from dotenv import load_dotenv
from steam_web_api import Steam
from rich import print

load_dotenv()

TARGET_CATEGORIES = (1, 9, 38)
STEAM_KEY = environ.get('STEAM_KEY')
OUT_DIRECTORY = 'out'

coop_games = []
coop_filename = path.join(OUT_DIRECTORY, "identified.txt")
failed_games = []
failed_filename = path.join(OUT_DIRECTORY, "failed.txt")
error_games = []
error_filename = path.join(OUT_DIRECTORY, "error.txt")

def write_list_to_file(game_list: list[str], filename: str) -> bool:
    with open(filename, 'w+') as file_writer:
        write_text = "\n".join(game_list)
        file_writer.write(write_text)

steam = Steam(STEAM_KEY)
search_result = steam.users.search_user('chainercygnus')
steam_id = search_result['player']['steamid']
games_reply = steam.users.get_owned_games(steam_id)
games = games_reply['games']

for game in games:
    try:
        app_id = f"{game['appid']}"
        app_details = steam.apps.get_app_details(app_id, filters="categories")
        if app_details[app_id]['success'] and app_details is not None and app_details[app_id]['data'] != []:
            for category in app_details[app_id]['data']['categories']:
                if category['id'] in TARGET_CATEGORIES and game['name'] not in coop_games:
                    coop_games.append(game['name'])
        else:
            failed_games.append(game['name'])
    except Exception as e:
        error_games.append(f"{game['name']} [{app_id}] :: {e}")
    sleep(randint(1,5))

write_list_to_file(coop_games, coop_filename)
write_list_to_file(failed_games, failed_filename)
write_list_to_file(error_games, error_filename)
