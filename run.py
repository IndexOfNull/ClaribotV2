import asyncio
import argparse
import json
from bot import Claribot

#Fancy command line stuff so we can control how the bot executes


parser = argparse.ArgumentParser(description='Runs the Discord bot.')
parser.add_argument('-d','--dev',help='Starts the bot in developer mode',const=False,nargs='?')
parser.add_argument('-s','--shard',help='Specify a shard for the bot to run on',nargs=2,metavar=('shard-id','shard-count'))

args = parser.parse_args()

#Work out variables

with open('bot.json','r') as r:
    settings = json.loads(r.read())
    dbPass = settings.pop('db_pass')
    db_name = settings.pop('db_name','claribot')
    db_location = settings.pop('db_ip','localhost')
    db_username = settings.pop('db_username','claribot_user')
    token = settings.pop('bot_token')

if args.dev:
    devMode = True
else:
    devMode = False

if not args.shard:
    args.shard = (None,None)
else:
    args.shard = (int(args.shard[0]),int(args.shard[1]))

#Asyncio stuff
loop = asyncio.get_event_loop()

bot = Claribot(loop=loop,shard_id=args.shard[0],shard_count=args.shard[1],db_name=db_name,db_ip=db_location,db_username=db_username,devMode=devMode,max_messages=10000,dbPass=dbPass,token=token)

#Run the bot, and try to close gracefuly on error.
if __name__ == '__main__':
    try:
        task = loop.create_task(bot.run())
        task.add_done_callback(functools.partial(main,loop))
        bot.own_task = task
        loop.run_until_complete(task)
        loop.run_forever()
    except (KeyboardInterrupt, RuntimeError):
        print('\nKeyboardInterrupt - Shutting down...')
        bot.die()
    finally:
        print('--Closing Loop--')
        loop.close()
