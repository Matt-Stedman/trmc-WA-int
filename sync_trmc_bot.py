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
TELEGRAM_API_KEY = "5678841436:AAEAOFewQu34NftfyK_9xxf5zDnzrPquD6k"
TELEGRAM_API_ID = '21634871'
TELEGRAM_API_HASH = 'b1f4fc0783c9037c45cd2006647ea606'
PHONE = '+447393186627'
CHAT_INVITE_LINK = "https://t.me/+G0icZz4yCsJhYTRk"

# creating a telegram session and assigning
# it to a variable client
client = TelegramClient('session', TELEGRAM_API_ID, TELEGRAM_API_HASH)
client.start()


# region - SYNC PROCESSES
def weekly_roundup() -> None:
    """Let's do the weekly round up.

    "Right guys, round up time! Let's see who's been kicking ass this week!
    then, for each goal:
    "Josh, your goal was X, and it looks like you're
        [smashing it! Nice work!]
        [getting there.... Let's push a bit if you have the time and energy!]
        [fucking failing, dude. Pull your socks up and get out there!]
    depending on progress (<20%, 50%, 100%).
    You did Y workouts this week.
    "
    then wipe the tally to round off the week.
    """

    # sending message using telegram client
    entity = client.get_entity(CHAT_INVITE_LINK)

    client.send_message(
        entity, "Right lads, Sunday round-up time 💪", parse_mode="html")
    goals_table = Table(
        AIRTABLE_API_KEY, 'appyvfZ8bqGlz2pkH', 'tbltjvyqmRyShiYXi')
    print(goals_table)

    for each_goal in goals_table.all():

        goal_name = each_goal["fields"]["Goal"]
        person = str(each_goal["fields"]["Person_name"][0])
        amount_expected = each_goal["fields"]["Times_per_week"]
        amount_performed = each_goal["fields"]["Count_this_week"]

        msg_construct = f"{person}, your goal was \""
        msg_construct += f"{goal_name} \"\n\n"
        if amount_performed >= amount_expected:
            msg_construct += f"You've SMASHED it this week with {amount_performed} / {amount_expected} performed 🔥."
        elif amount_performed >= round(amount_expected / 2):
            msg_construct += f"You're getting there this week with {amount_performed} / {amount_expected} so far. Try to get another session in today mate 😉."
        elif amount_performed > 0:
            msg_construct += f"You've fucked it mate. Get off your ass and stop making excuses. 💩 You only did {amount_expected} / {amount_performed} this week."
        else:
            last_worked_out_on = each_goal["fields"]["Last_worked_out"]
            msg_construct += f"Mate, are you even trying? You've not worked out AT ALL this week 😡. You last worked out on {last_worked_out_on}."
        client.send_message(entity, msg_construct, parse_mode="html")


def reset_table_at_midnight():
    """Reset the count at midnight"""
    goals_table = Table(
        AIRTABLE_API_KEY, 'appyvfZ8bqGlz2pkH', 'tbltjvyqmRyShiYXi')
    for each_goal in goals_table.iterate():
        goals_table.update(each_goal, {"Worked_out_today": False})


# endregion

# region - ASYNC PROCESSES


async def handle_iworkedout(event):
    """Handle the /iworkedout message to auto-update the Airtable and offer a note of encouragement."""
    from_user = await event.client.get_entity(event.from_id)
    from_user_phone = str(from_user.phone).replace("+", "")
    print(f"Nice job {from_user_phone}")

    people_table = Table(
        AIRTABLE_API_KEY, 'appyvfZ8bqGlz2pkH', 'tblyGN4myp1IkGjhS')
    goals_table = Table(
        AIRTABLE_API_KEY, 'appyvfZ8bqGlz2pkH', 'tbltjvyqmRyShiYXi')

    nice_messages = ["Good job dude!", "Fucking smashing it, mate 💪",
                     "Ohhhhhh momma!", "God you're so frekin' amazing!", "Fuck. Yes.", "Legend 😉"]

    for person in people_table.all():
        print(str(person["fields"]["Phone_number"]))
        if str(from_user_phone).replace(" ", "") == str(person["fields"]["Phone_number"]).replace("+", ""):
            # Handle table
            goal = goals_table.first(formula=match(
                {"Person_name": person["fields"]["Name"]}))
            now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S:000Z")
            update_details = {"Worked_out_today": True,
                              "Last_worked_out": now_time}
            print(goal["id"])
            print(update_details)
            goals_table.update(
                goal["id"], update_details)

            # # Handle image - TODO
            # if event.message.photo or event.message.video:
            #     path = await event.message.download_media()
            #     print("File saved to", path)
            #     goals_table.update(goal, {"Worked_out_today": True})

            # Handle "nice work bud" message
            entity = await client.get_entity(CHAT_INVITE_LINK)
            await client.send_message(entity, random.choice(nice_messages), parse_mode="html")
            await client.send_message("me", random.choice(nice_messages), parse_mode="html")


@client.on(events.NewMessage)
async def handle_messages(event):
    """Wrapper that handles all messages in the chat, with only specific ones being listened for"""
    print("Hello...")
    await event.client.get_entity(event.from_id)
    if "/iworkedout" in event.message.text or "/iworkedout" in event.message.message:
        print("2")
        await handle_iworkedout(event=event)

# endregion


def schedule_runner():
    """Just run the scheduler"""
    while True:
        schedule.run_pending()
        print("chirp")
        time.sleep(60)  # wait one minute


def message_handler_runner():
    """Just run the message handler"""
    client.run_until_disconnected()


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
    schedule.every(10).seconds.do(weekly_roundup)
    schedule.every().day.at("00:01").do(reset_table_at_midnight)
    multiprocessing.Process(target=schedule_runner).start()

    # Run the auto-responses in a seperate process
    multiprocessing.Process(target=message_handler_runner).start()

    # disconnecting the telegram session
    client.disconnect()


if __name__ == "__main__":
    main()
