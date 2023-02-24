import asyncio
from pyrogram import Client, enums
from pyrogram.errors import FloodWait, UserNotParticipant
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

from database.join_reqs import JoinReqs
from config import ADMINS, FORCE_MSG, REQ_CHANNEL, JOIN_REQS_DB, FORCE_SUB_CHANNEL as AUTH_CHANNEL

from logging import getLogger
logger = getLogger(__name__)

INVITE_LINK = None
db = JoinReqs

async def ForceSub(bot: Client, update: Message):
    global INVITE_LINK
    if update.from_user.id in ADMINS:
        return True

    if not AUTH_CHANNEL and not REQ_CHANNEL:
        return True

    # Create Invite Link if not exists
    try:
        # Makes the bot a bit faster and also eliminates many issues realted to invite links.
        if INVITE_LINK is None:
            f_chat =  REQ_CHANNEL if REQ_CHANNEL else AUTH_CHANNEL
            req_true = True if REQ_CHANNEL else False
            create_invite = await bot.create_chat_invite_link(chat_id=f_chat, creates_join_request=req_true)
            INVITE_LINK = create_invite.invite_link            
        else:
            invite_link = INVITE_LINK
    except FloodWait as e:
        await asyncio.sleep(e.x)
        fix_d = await ForceSub(bot, update)
        return fix_d     
    except Exception as err:
        print(f"Unable to do Force Subscribe to {REQ_CHANNEL}\n\nError: {err}\n\n")
        await update.reply(text="Something went Wrong.")            
        return False

    # Mian Logic
    if REQ_CHANNEL and db().isActive():
        try:
            # Check if User is Requested to Join Channel
            user = await db().get_user(update.from_user.id)
            if user and user["user_id"] == update.from_user.id:
                return True
        except Exception as e:
            logger.exception(e, exc_info=True)
            await update.reply(text="Something went Wrong.")               
            return False

    try:
        if not AUTH_CHANNEL:
            raise UserNotParticipant
        # Check if User is Already Joined Channel
        fcht_ids = AUTH_CHANNEL if not REQ_CHANNEL and not db().isActive() else REQ_CHANNEL
        user = await bot.get_chat_member(chat_id=fcht_ids, user_id=update.from_user.id)                
        if user.status == enums.ChatMemberStatus.BANNED:
            await bot.send_message(chat_id=update.from_user.id, text="Sorry Sir, You are Banned to use me.")              
            return False
        else:
            return True
    except UserNotParticipant:        
        buttons = [[
            InlineKeyboardButton("📢 Request to Join Channel 📢", url=invite_link)
            ],[
            InlineKeyboardButton(" 🔄 Try Again 🔄 ", url = f"https://t.me/{bot.username}?start={message.command[1]}")
        ]]         
         
        await update.reply(
            text=FORCE_MSG.format(
                first = update.from_user.first_name,
                last = update.from_user.last_name,
                username = None if not update.from_user.username else '@' + update.from_user.username,
                mention = update.from_user.mention,
                id = update.from_user.id
            ),
            quote=True,
            reply_markup=InlineKeyboardMarkup(buttons),           
        )
        return False

    except FloodWait as e:
        await asyncio.sleep(e.x)
        fix_d = await ForceSub(bot, update)
        return fix_d

    except Exception as err:
        print(f"Something Went Wrong! Unable to do Force Subscribe.\nError: {err}")
        await update.reply("Something went Wrong.")            
        return False


def set_global_invite(url: str):
    global INVITE_LINK
    INVITE_LINK = url


