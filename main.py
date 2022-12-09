#!/usr/bin/env python
# pylint: disable=unused-argument, wrong-import-position
# This program is dedicated to the public domain under the CC0 license.

# importing all required libraries
from telethon.sync import TelegramClient, events

from pyairtable import Table
from pyairtable.formulas import match
import time
import schedule
import random
import asyncio

from datetime import datetime
import multiprocessing
import logging
logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)

# import os
# airtable_api_key = os.environ["AIRTABLE_API_TOKEN"] use export for this soon!
AIRTABLE_API_KEY = "patiXB5YDfZ31eYYV.8f40ce718cf811562c2d1e6092f157b0a54ec6b610e1d546464544bf44503cc7"
TELEGRAM_BOT_TOKEN = "5678841436:AAEAOFewQu34NftfyK_9xxf5zDnzrPquD6k"
TELEGRAM_API_ID = '21634871'
TELEGRAM_API_HASH = 'b1f4fc0783c9037c45cd2006647ea606'
PHONE = '+447393186627'
CHAT_INVITE_LINK = "https://t.me/+G0icZz4yCsJhYTRk"
GROUP = -868831158
BOT_IS_FREE = True

# creating a telegram session and assigning
# it to a variable client
client = TelegramClient('bot', TELEGRAM_API_ID, TELEGRAM_API_HASH).start(
    bot_token=TELEGRAM_BOT_TOKEN)
client.connect()

# region - SYNC PROCESSES


def weekly_roundup() -> None:
    """Let's do the weekly round up.

    "Right guys, round up time! Let's see who's been kicking ass this week!
    then, for each goal:
    "Josh, your goal was X, and it looks like you're
        [smashing it! Nice work!]
        [getting there.... Let's push a bit if you have the time and energy!]
        [fucking failing, dude. Pull your socks up and get out there!]
    depending on progress (<20%, 50%, 100%).y
    You did Y workouts this week.
    "
    then wipe the tally to round off the week.
    """
    global BOT_IS_FREE
    while not BOT_IS_FREE:
        print("fuck")
        asyncio.sleep(1)

    BOT_IS_FREE = False
    # sending message using telegram client
    print("started here")
    # entity = client.get_entity(CHAT_INVITE_LINK)
    if not client.is_connected():
        client.connect()
    
    client.send_message(
        GROUP, "Right lads, Sunday round-up time 💪", parse_mode="html")
    print("then here")
    goals_table = Table(
        AIRTABLE_API_KEY, 'appyvfZ8bqGlz2pkH', 'tbltjvyqmRyShiYXi')
    print(goals_table)

    for each_goal in goals_table.all():

        goal_name = each_goal["fields"]["Goal"]
        person = str(each_goal["fields"]["Person_name"][0])
        amount_expected = each_goal["fields"]["Times_per_week"]
        amount_performed = each_goal["fields"]["Count_this_week"]

        msg_construct = f"{person}, your goal was \""

        msg_construct += f"{goal_name} \"\n"
        if amount_performed >= amount_expected:
            msg_construct += "⭐⭐⭐⭐⭐\n\n"
            msg_construct += f"You've SMASHED it this week with {amount_performed} / {amount_expected} performed 🔥."
        elif amount_performed >= round(amount_expected / 2):
            msg_construct += "⭐⭐⭐\n\n"
            msg_construct += f"You're getting there this week with {amount_performed} / {amount_expected} so far. Try to get another session in today mate 😉."
        elif amount_performed > 0:
            msg_construct += "⭐\n\n"
            msg_construct += f"Come on mate. Get off your ass and stop making excuses. You only did {amount_performed} / {amount_expected} this week."
        else:
            last_worked_out_on = each_goal["fields"]["Last_worked_out"]
            msg_construct += "💩\n\n"
            msg_construct += f"Mate, are you even trying? You've not worked out AT ALL this week 😡. You last worked out on {last_worked_out_on}."
        client.send_message(GROUP, msg_construct, parse_mode="html")

    asyncio.sleep(3)
    print("Done!")
    BOT_IS_FREE = True


def reset_table_at_midnight():
    """Reset the count at midnight"""
    global BOT_IS_FREE
    while not BOT_IS_FREE:
        asyncio.sleep(1)
    BOT_IS_FREE = False
    goals_table = Table(
        AIRTABLE_API_KEY, 'appyvfZ8bqGlz2pkH', 'tbltjvyqmRyShiYXi')
    for each_goal in goals_table.iterate():
        goals_table.update(each_goal, {"Worked_out_today": False})
    BOT_IS_FREE = True


# endregion

# region - ASYNC PROCESSES


async def handle_iworkedout(event):
    """Handle the /iworkedout message to auto-update the Airtable and offer a note of encouragement."""
    print(f"Nice job {event}")
    from_user = await event.get_sender()
    print(f"Nice job {from_user.username}")
    from_username = from_user.username

    people_table = Table(
        AIRTABLE_API_KEY, 'appyvfZ8bqGlz2pkH', 'tblyGN4myp1IkGjhS')
    goals_table = Table(
        AIRTABLE_API_KEY, 'appyvfZ8bqGlz2pkH', 'tbltjvyqmRyShiYXi')
    nice_messages = ["Good job dude!", "Fucking smashing it, mate 💪",
                     "Ohhhhhh momma!", "God you're so frekin' amazing!", "Fuck. Yes.", "Legend 😉"]

    person = people_table.first(formula=match(
        {"Telegram_username": from_username}))
    print(person)
    # a = [
    #     {'id': 'rec7V5VWhBaRxlZlY', 'createdTime': '2022-12-04T16:54:17.000Z', 'fields': {'Name': 'Stephan', 'Phone_number': '+491729886765', 'Goals': ['rec8iblgcDRaqWMRf']}},
    #     {'id': 'recOBIlKLBGGDsURB', 'createdTime': '2022-12-04T16:54:17.000Z', 'fields': {'Name': 'Josh', 'Phone_number': '+447310342171','Goals': ['recYzpaUVw4FjkIgJ'], 'Telegram_username': 'JuicyGoosie'}},
    #     {'id': 'rechipCgfQ6GSCDYE', 'createdTime': '2022-12-04T16:54:17.000Z', 'fields': {'Name': 'Matt', 'Phone_number': '+447393186627', 'Goals': ['recPVqdmEKptAPUxV'], 'Telegram_username': 'Matt_Stedman'}}
    #     ]
    if "Telegram_username" in person["fields"].keys():
        print(str(person["fields"]["Telegram_username"]))
        if str(from_username).replace("@", "") == str(person["fields"]["Telegram_username"]).replace("@", ""):
            goal = goals_table.first(formula=match(
                {"Person_name": person["fields"]["Name"]}))
            now_time = datetime.now()
            if "Last_worked_out" in goal["fields"].keys():
                last_worked_out_on = goal["fields"]["Last_worked_out"]
                last_worked_out_on = datetime.strptime(
                    last_worked_out_on, "%Y-%m-%dT%H:%M:%S.000Z").date()
                print("Last worked out on: ", last_worked_out_on)
                print("Now date is: ", now_time.date())
                if last_worked_out_on < now_time.date():
                    worked_out_today = False
                else:
                    worked_out_today = True
            else:
                worked_out_today = False
            if worked_out_today:
                await client.send_message(GROUP,  "You've already worked out today.", parse_mode="html")
            else:
                # Handle table
                count_this_week = goal["fields"]["Count_this_week"]
                update_details = {
                    "Last_worked_out": now_time.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                    "Count_this_week": count_this_week + 1,
                }
                print(goal["id"])
                print(update_details)
                goals_table.update(
                    goal["id"], update_details)

                # # Handle image - TODO
                # if event.message.photo or event.message.video:
                #     path = await event.message.download_media()
                #     print("File saved to", path)
                #     goals_table.update(goal, {"Worked_out_today": True})

                print("Sending cheery message")

                # Handle "nice work bud" message
                await client.send_message(GROUP,  random.choice(nice_messages), parse_mode="html")

                print("Cheery message sent!")


@client.on(events.NewMessage)
async def handle_messages(event):
    """Wrapper that handles all messages in the chat, with only specific ones being listened for"""
    print("Hello...")

    global BOT_IS_FREE
    while not BOT_IS_FREE:
        print("fuck")
        asyncio.sleep(1)

    BOT_IS_FREE = False
    await event.client.get_entity(event.from_id)
    if "/iworkedout" in event.message.text or "/iworkedout" in event.message.message:
        print("2")
        await handle_iworkedout(event=event)

    BOT_IS_FREE = True
# endregion


def schedule_runner():
    """Just run the scheduler"""
    while True:
        schedule.run_pending()
        print("chirp")
        asyncio.sleep(10)  # wait one minute


# def message_handler_runner():
#     """Just run the message handler"""
#     client.run_until_disconnected()

def free_bot_every_ten_minutes():
    """ Just in case our bot has been trapped in an infinite loop somewhere"""
    global BOT_IS_FREE
    BOT_IS_FREE = True


def main() -> None:
    # connecting and building the session

    # in case of script ran first time it will
    # ask either to input token or otp sent to
    # number or sent or your telegram id
    if not client.is_user_authorized():

        client.send_code_request(PHONE)

        # signing in the client
        client.sign_in(PHONE, input('Enter the code: '))

    # Run the scheduled events in a process
    schedule.every(1).minutes.do(weekly_roundup)
    schedule.every().day.at("00:01").do(reset_table_at_midnight)
    schedule.every(10).minutes.do(free_bot_every_ten_minutes)
    multiprocessing.Process(target=schedule_runner).start()

    # Run the auto-responses in a seperate process
    client.run_until_disconnected()
    while True:
        global BOT_IS_FREE
        while not BOT_IS_FREE:
            print("fuck")
            asyncio.sleep(1)
        
        if not client.is_connected():
            client.run_until_disconnected()
            print("Disconnected, let's reconnect")

    # disconnecting the telegram session
    client.disconnect()


if __name__ == "__main__":
    main()
