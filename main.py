import datetime
import random
import asyncio 

import pytz
from pyairtable import Table
from pyairtable.formulas import match
from pyairtable.utils import attachment
from telegram import Update
from telegram.ext import (ApplicationBuilder, CommandHandler, ContextTypes,
                          MessageHandler, filters)

AIRTABLE_API_KEY = "patiXB5YDfZ31eYYV.8f40ce718cf811562c2d1e6092f157b0a54ec6b610e1d546464544bf44503cc7"
TELEGRAM_BOT_TOKEN = "5678841436:AAEAOFewQu34NftfyK_9xxf5zDnzrPquD6k"
TELEGRAM_API_ID = '21634871'
TELEGRAM_API_HASH = 'b1f4fc0783c9037c45cd2006647ea606'
PHONE = '+447393186627'
CHAT_INVITE_LINK = "https://t.me/+G0icZz4yCsJhYTRk"
GROUP = -868831158


# region SCHEDULED MESSAGES

async def weekly_roundup(context: ContextTypes.DEFAULT_TYPE):
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

    # sending message using telegram client
    print("Sending weekly roundup...")
    await context.bot.send_message(
        chat_id=GROUP, text="Right lads, Sunday round-up time 💪")

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
        await context.bot.send_message(chat_id=GROUP, text=msg_construct)

    print("Done!")


async def morning_reminder(context: ContextTypes.DEFAULT_TYPE):
    """Let's do a morning reminder for everyone to workout."""

    goals_table = Table(
        AIRTABLE_API_KEY, 'appyvfZ8bqGlz2pkH', 'tbltjvyqmRyShiYXi')
    people_table = Table(
        AIRTABLE_API_KEY, 'appyvfZ8bqGlz2pkH', 'tblyGN4myp1IkGjhS')
    print(goals_table)
    now_time = datetime.datetime.now()

    whose_not_worked_out = []
    for each_goal in goals_table.all():
        if "Last_worked_out" in each_goal["fields"].keys():
            last_worked_out_on = each_goal["fields"]["Last_worked_out"]
            last_worked_out_on = datetime.datetime.strptime(
                last_worked_out_on, "%Y-%m-%dT%H:%M:%S.000Z").date()
            print("Last worked out on: ", last_worked_out_on)
            print("Now date is: ", now_time.date())
            if last_worked_out_on < now_time.date():
                worked_out_today = False
            else:
                worked_out_today = True
        else:
            worked_out_today = False

        if not worked_out_today:
            # get their telegram info
            # TODO wrap in a TRY/EXCEPT
            whose_not_worked_out.append(each_goal["fields"]["Person_name"][0])

    msg_construct = random.choice(
        ["Morning lads, ", "Hey guys 🤩, ", "Rise and shine fuckers, ", "Sup peepz, "])
    if len(whose_not_worked_out) == 0:
        msg_construct += "looks like everyone's already worked out today. Coolio."
    elif len(whose_not_worked_out) == len(each_goal):
        msg_construct += "don't forget to workout today if it's on your todo list 😉."
    else:
        for i, each in enumerate(whose_not_worked_out):
            print(whose_not_worked_out)
            if i == len(whose_not_worked_out) - 1:
                msg_construct += " and "
            elif i != 0:
                msg_construct += ", "
            msg_construct += each
        msg_construct += " all need to work out. Don't forget 💪"
    await context.bot.send_message(chat_id=GROUP, text=msg_construct)
    print("Done!")


async def evening_reminder(context: ContextTypes.DEFAULT_TYPE):
    """Let's do an evening reminder for everyone to workout."""

    goals_table = Table(
        AIRTABLE_API_KEY, 'appyvfZ8bqGlz2pkH', 'tbltjvyqmRyShiYXi')
    people_table = Table(
        AIRTABLE_API_KEY, 'appyvfZ8bqGlz2pkH', 'tblyGN4myp1IkGjhS')
    print(goals_table)

    now_time = datetime.datetime.now()

    whose_not_worked_out = []
    for each_goal in goals_table.all():
        if "Last_worked_out" in each_goal["fields"].keys():
            last_worked_out_on = each_goal["fields"]["Last_worked_out"]
            last_worked_out_on = datetime.datetime.strptime(
                last_worked_out_on, "%Y-%m-%dT%H:%M:%S.000Z").date()
            print("Last worked out on: ", last_worked_out_on)
            print("Now date is: ", now_time.date())
            if last_worked_out_on < now_time.date():
                worked_out_today = False
            else:
                worked_out_today = True
        else:
            worked_out_today = False

        if not worked_out_today:
            # get their telegram info
            # TODO wrap in a TRY/EXCEPT
            whose_not_worked_out.append(each_goal["fields"]["Person_name"][0])

    msg_construct = random.choice(
        ["Evening lads, ", "Hey guys 🤩, ", "Yo fuckers, ", "Sup peepz, "])
    if len(whose_not_worked_out) == 0:
        msg_construct += "looks like everyone's already worked out today. Coolio."
    elif len(whose_not_worked_out) == len(each_goal):
        msg_construct += "don't forget to workout today if it's on your todo list 😉."
    else:
        for i, each in enumerate(whose_not_worked_out):
            if i == len(whose_not_worked_out) - 1:
                msg_construct += " and "
            else:
                msg_construct += ", "
            msg_construct += each
        msg_construct += " all need to work out. Don't forget 💪"
    await context.bot.send_message(chat_id=GROUP, text=msg_construct)
    print("Done!")

# endregion

# region RESPONSIVE MESSAGES


async def image_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Media recieved..")
    should_process_goal = await handle_iworkedout(update, context)
    if should_process_goal is not None:
        print("nice")
        if update.message.photo is not None or len(update.message.photo) is not None:
            file = update.message.photo[-1].file_id
            obj = await context.bot.get_file(file)
            goals_table = Table(
                AIRTABLE_API_KEY, 'appyvfZ8bqGlz2pkH', 'tbltjvyqmRyShiYXi')
            print(should_process_goal)

            record = goals_table.get(record_id=should_process_goal)
            if "Proofs" in record["fields"]:
                current_attachments = record["fields"]["Proofs"]
            else:
                current_attachments = []

            current_attachments.append(attachment(obj.file_path))
            update_details = {"Proofs": current_attachments}
            goals_table.update(should_process_goal, update_details)

            await update.message.reply_text("I've also uploaded this to the database.. 😉")
    print("Media processed if possible")


async def handle_iworkedout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Handle the /iworkedout message to auto-update the Airtable and offer a note of encouragement."""
    print(f"{update.effective_user.username} has just worked out!")
    from_username = update.effective_user.username

    people_table = Table(
        AIRTABLE_API_KEY, 'appyvfZ8bqGlz2pkH', 'tblyGN4myp1IkGjhS')
    goals_table = Table(
        AIRTABLE_API_KEY, 'appyvfZ8bqGlz2pkH', 'tbltjvyqmRyShiYXi')
    nice_messages = ["Good job dude!", "Fucking smashing it, mate 💪",
                     "Ohhhhhh momma!", "God you're so frekin' amazing! 🤤", "Fuck. Yes.", "Legend 😉"]

    person = people_table.first(formula=match(
        {"Telegram_username": from_username}))
    print(person)
    if "Telegram_username" in person["fields"].keys():
        print(str(person["fields"]["Telegram_username"]))
        if str(from_username).replace("@", "") == str(person["fields"]["Telegram_username"]).replace("@", ""):

            # Handle finding your goals
            goal = goals_table.first(formula=match(
                {"Person_name": person["fields"]["Name"]}))
            now_time = datetime.datetime.now()
            if "Last_worked_out" in goal["fields"].keys():
                last_worked_out_on = goal["fields"]["Last_worked_out"]
                last_worked_out_on = datetime.datetime.strptime(
                    last_worked_out_on, "%Y-%m-%dT%H:%M:%S.000Z").date()
                print("Last worked out on: ", last_worked_out_on)
                print("Now date is: ", now_time.date())
                if last_worked_out_on < now_time.date():
                    worked_out_today = False
                else:
                    worked_out_today = True
            else:
                worked_out_today = False

            # Handle table
            if worked_out_today:
                await update.message.reply_text("You've already worked out today.")
                print("They've already worked out")
                return None
            else:

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
                await update.message.reply_text(random.choice(nice_messages))

                print("Cheery message sent!")
                return goal["id"]


async def start_auto_messaging(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set up the scheduled message collection"""
    chat_id = update.message.chat_id
    context.job_queue.run_daily(morning_reminder, time=datetime.time(
        hour=8, minute=0, tzinfo=pytz.timezone('GMT')), days=(0, 1, 2, 3, 4, 5, 6), chat_id=chat_id)
    context.job_queue.run_daily(evening_reminder, time=datetime.time(
        hour=19, minute=0, tzinfo=pytz.timezone('GMT')), days=(0, 1, 2, 3, 4, 5, 6), chat_id=chat_id)
    context.job_queue.run_daily(weekly_roundup, time=datetime.time(
        hour=15, minute=25, tzinfo=pytz.timezone('GMT')), days=(0), chat_id=chat_id)
# endregion


async def main() -> None:
    """Main loop ;)"""
    async with aiohttp.ClientSession() as session:
        app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
        app.add_handler(CommandHandler("auto", start_auto_messaging))
        app.add_handler(CommandHandler("iworkedout", handle_iworkedout))
        app.add_handler(MessageHandler(filters=filters.Caption(
            ["iworkedout", "/iworkedout"]), callback=image_handler))

        app.run_polling(timeout=30)


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())