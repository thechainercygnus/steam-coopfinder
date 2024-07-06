from os import environ, path, mkdir
from time import sleep
from random import randint
import logging

from steam_web_api import Steam
from rich import print

APPLICATION_NAME = "coopfinder"
TARGET_CATEGORIES = (1, 9, 38)
STEAM_KEY = environ.get('STEAM_KEY')
STEAM_BASE_USER = environ.get('STEAM_BASE_USER')
OUT_DIRECTORY = 'out'
LOG_DIRECTORY = 'log'
LOG_LEVEL = environ.get('LOG_LEVEL')
LOG_PATH = path.join(LOG_DIRECTORY, APPLICATION_NAME)

if LOG_LEVEL == 'DEBUG':
    log_level_setter = logging.DEBUG
else:
    log_level_setter = logging.INFO

log_writer = logging.getLogger("coopfinder.log")
log_writer.setLevel(log_level_setter)
file_handler = logging.FileHandler(LOG_PATH)
file_handler.setLevel(log_level_setter)
formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
file_handler.setFormatter(formatter)
log_writer.addHandler(file_handler)

coop_filename = "identified.txt"
failed_filename = "failed.txt"
error_filename = "error.txt"

def write_game_to_file(game_name: str, filename: str) -> None:
    log_message = f"Writing [{game_name}] to [{filename}]"
    log_writer.info(log_message)
    with open(filename, 'a+') as file_appender:
        file_appender.write(f"{game_name}\n")

def get_steam_user_id_from_name(steam_username: str) -> str:
    steam = Steam(STEAM_KEY)
    search_result = steam.users.search_user(steam_username)
    steam_id = search_result['player']['steamid']
    return steam_id

def get_base_user_friendlist() -> list[str]:
    steam = Steam(STEAM_KEY)
    user_id = get_steam_user_id_from_name(STEAM_BASE_USER)
    friendslist = steam.users.get_user_friends_list(user_id)['friends']
    return [friend['steamid'] for friend in friendslist]


def build_steam_catalog_for_user(steam_id: str):
    player_found_games = []
    
    steam = Steam(STEAM_KEY)
    user_details = steam.users.get_user_details(steam_id)
    persona_name = user_details['player']['personaname']
    games_reply = steam.users.get_owned_games(steam_id)
    games = games_reply['games']

    player_directory = path.join(OUT_DIRECTORY, persona_name)
    if not path.exists(player_directory):
        mkdir(player_directory)

    player_coop_filename = path.join(player_directory, coop_filename)
    player_failed_filename = path.join(player_directory, failed_filename)
    player_error_filename = path.join(player_directory, error_filename)

    for game in games:
        log_message = f"{persona_name} :: Beginning check process for {game['name']}"
        log_writer.debug(log_message)
        try:
            app_id = f"{game['appid']}"
            app_details = steam.apps.get_app_details(app_id, filters="categories")
            log_message = f"{persona_name} :: Details obtained : {game['name']}"
            log_writer.info(log_message)
            log_writer.debug(app_details)
            if app_details[app_id]['success'] and app_details is not None and app_details[app_id]['data'] != []:
                for category in app_details[app_id]['data']['categories']:
                    if category['id'] in TARGET_CATEGORIES and game['name'] not in player_found_games:
                        log_message = f"{persona_name} :: Match found : {category['description']}"
                        log_writer.debug(log_message)
                        player_found_games.append(game['name'])
                        write_game_to_file(game['name'], player_coop_filename)
            else:
                write_game_to_file(game['name'], player_failed_filename)
        except Exception as e:
            write_game_to_file(game['name'], player_error_filename)
        sleep(randint(1,5))

if __name__ == "__main__":
    base_user_steam_id = get_steam_user_id_from_name(STEAM_BASE_USER)
    friendslist = get_base_user_friendlist()
    build_steam_catalog_for_user(base_user_steam_id)
    for friend in friendslist:
        build_steam_catalog_for_user(friend)