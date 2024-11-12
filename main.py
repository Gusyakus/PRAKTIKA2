import vk_api
import json
import time
import os
import aiohttp
import asyncio
from dotenv import load_dotenv
from vk_api.exceptions import ApiError

load_dotenv()
# ID пользователей Никита, Маргарита, Екатерина, Татьяна
# '164679738', '419376445', '472133870', '386272361'
user_ids = [
    '172350665', '229180632', '145195585', '193887357', 
    '386272361', '204720239', '162225997', '860446539', 
    '472133870', '195614586', '825545292', '750743366', 
    '637593527', '299106540', '164679738', '101098087', 
    '239666833', '342040017', '205762499', '165171730', 
    '270780454', '155290829', '151413977', '62269831', 
    '253407490', '192574298', '144399122', '419376445', 
    '508644412', '396854328'
]
access_token = "vk1.a.bFrQTvV6NNHXNrLqtH2_cJ8re-r-4SnlHSxZACl7x7hW-X_uQ-LOmvnXxwBcrQEMY0L6uXwFIxdu5N7_4ElU-sQluCoEGKM8EiJyz2y8oylvyUiSr3JyyA2PGM6LOoLC2hAeJAPHrFEWKtib_QJ0zyA6ykA_-zC-zcP3TbajWlggQIDFhbtJ0dNFU2DFuhy4ZE5Py2KjTEbXWQzahhyRzA"

vk_session = vk_api.VkApi(token=access_token)
vk = vk_session.get_api()

# Функция для получения информации о пользователе
def fetch_user_details(user_id):
    try:
        user_details = vk.users.get(user_ids=user_id)[0]
        return {
            "id": user_id,
            "first_name": user_details['first_name'],
            "last_name": user_details['last_name']
        }
    except ApiError as e:
        print(f"Ошибка получения данных пользователя (ID: {user_id}): {e}")
        return None

# Функция для получения списка друзей
def fetch_friends(user_id):
    try:
        friends_list = vk.friends.get(user_id=user_id, count=100)
        return friends_list.get('items', [])
    except ApiError as e:
        print(f"Ошибка получения списка друзей (ID: {user_id}): {e}")
        return []

# Асинхронная функция для обработки пользователя и записи данных в файл
async def handle_user(user_id, output_file):
    user_details = fetch_user_details(user_id)
    if not user_details:
        return

    user_info = {
        "id": user_details["id"],
        "friends": []
    }

    friends_list = fetch_friends(user_id)

    for friend_id in friends_list[:100]:  # Ограничение на 100 друзей
        friend_details = fetch_user_details(friend_id)
        if not friend_details:
            continue

        friend_info = {
            "id": friend_id,
            "name": f"{friend_details['first_name']} {friend_details['last_name']}",
            "friends_of_friend": []
        }

        friends_of_friend_list = fetch_friends(friend_id)

        for fof_id in friends_of_friend_list[:100]:  # Ограничение на 100 друзей друзей
            fof_details = fetch_user_details(fof_id)
            if not fof_details:
                continue

            friend_info["friends_of_friend"].append({
                "id": fof_id,
                "name": f"{fof_details['first_name']} {fof_details['last_name']}"
            })

        user_info["friends"].append(friend_info)

    # Запись данных в файл по мере их получения
    output_file.write(json.dumps({f"{user_details['first_name']} {user_details['last_name']}": user_info}, ensure_ascii=False, indent=4) + ',\n')

async def main():
    team_members = {
        '172350665', '229180632', '145195585', '193887357',
        '386272361', '204720239', '162225997', '860446539',
        '472133870', '195614586', '825545292', '750743366',
        '637593527', '299106540', '164679738', '101098087',
        '239666833', '342040017', '205762499', '165171730',
        '270780454', '155290829', '151413977', '62269831',
        '253407490', '192574298', '144399122', 
        '419376445','508644412','396854328'
    }

    with open('team_data.json', 'w', encoding='utf-8') as output_file:
        output_file.write('{"team": {\n')

        tasks = [handle_user(user_id, output_file) for user_id in team_members]
        await asyncio.gather(*tasks)

        output_file.write('\n}}')

if __name__ == '__main__':
    asyncio.run(main())