# \\       Made by @LucifSD02 on Telegram       //
#  \\   https://github.com/TgCatUB/catuserbot  //
#   \\    @Jisan7509 -- Github.com/Jisan09    //
#    \\       Plugin for @catuserbot         //
#     ````````````````````````````````````````

import os

from userbot import catub

from ..core.managers import edit_delete, edit_or_reply
from ..helpers.chatbot import (del_convo, generate_dalle_image,
                               generate_gpt_response)
from ..helpers.utils import reply_id
from ..sql_helper.globals import addgvar, delgvar, gvarstatus

plugin_category = "tools"


MODELS = ["gpt-3.5-turbo", "gpt-3.5-turbo-0301"]
SIZE = ["256", "512", "1024"]


@catub.cat_cmd(
    pattern="gpt(?: |$)(.*)",
    command=("gpt", plugin_category),
    info={
        "header": "Generate GPT response with prompt",
        "description": "Use {tr}gpt followed by a prompt to generate a GPT response using the provided text",
        "flags": {
            "m": "To change model of ai.",
            "s": "To add system message.",
            "ds": "To delete system message.",
            "dc": "To delete context of given chat.",
        },
        "usage": [
            "{tr}gpt <text/reply>",
            "{tr}gpt -m <model name>",
            "{tr}gpt -s <system message>",
            "{tr}gpt -ds",
            "{tr}gpt -dc",
        ],
        "examples": [
            "{tr}gpt write a paragraph on cat",
            "{tr}gpt -m gpt-3.5-turbo-0301",
            "{tr}gpt -s Write every answer in an extremely angry tone , use swear words and insults wherever you see fit",
        ],
        "available models": MODELS,
    },
)
async def gpt_response_with_prompt(event):
    "Generate a GPT response using the provided text using Openai Api"
    text = event.pattern_match.group(1)
    reply = await event.get_reply_message()
    model_text = "**Available models:**\n\n"
    chat_id = event.chat_id

    # Flag to change model of ai
    if "-m" in text:
        flag = text.replace("-m", "").strip()
        if not flag or flag not in MODELS:
            for index, name in enumerate(MODELS, 1):
                model_text += f"**{index}.** `{name}`\n"
            return await edit_delete(event, model_text, 50)
        addgvar("CHAT_MODEL", flag)
        return await edit_delete(event, f"__Chat model changed to : **{flag}**__")

    # Flag to add system message
    elif "-s" in text:
        flag = text.replace("-s", "").strip()
        if not flag:
            return await edit_delete(
                event, "__Pass the system message along with flag.__"
            )
        addgvar("SYSTEM_MESSAGE", flag)
        del_convo(chat_id)
        return await edit_delete(event, f"__System message changed to :__\n\n`{flag}`")

    # Flag to delete system message
    elif "-ds" in text:
        SYSTEM_MESSAGE = gvarstatus("SYSTEM_MESSAGE") or None
        if SYSTEM_MESSAGE:
            del_convo(chat_id)
            delgvar("SYSTEM_MESSAGE")
            return await edit_delete(event, "__System message cleared.__")
        return await edit_delete(event, "__There's no system message set for GPT.__")

    # Flag to delete context of given chat
    elif "-dc" in text:
        response = del_convo(chat_id, True)
        return await edit_delete(event, response)

    # Check if text given else take text from reply message
    if not text and reply:
        text = reply.text
    if not text:
        return await edit_delete(event, "**ಠ∀ಠ Gimmi text**")

    await edit_or_reply(event, "__Generating answer...__")
    gpt_response = await generate_gpt_response(text, chat_id)
    await edit_or_reply(event, gpt_response)


@catub.cat_cmd(
    pattern="dalle(?: |$)(.*)",
    command=("dalle", plugin_category),
    info={
        "header": "Generate image using DALL-E",
        "description": "Generate an image using the provided text or Generate semiler image",
        "flags": {
            "n": "To change number of output.",
            "s": "To change pixel size of ai.",
            "e": "To edit the replied media with instructions.",
            "v": "To show variations of replied Image.",
        },
        "usage": [
            "{tr}dalle <text/reply>",
            "{tr}dalle -n <1-10>",
            "{tr}dalle -s <pixel size>",
            "{tr}dalle -e <reply to image with instructions>",
            "{tr}dalle -v <reply to image>",
        ],
        "examples": [
            "{tr}dalle cat & dog riding bicycle",
            "{tr}dalle -n 3",
            "{tr}dalle -s 512",
            "{tr}dalle -e write cat on it <reply to an Image>.",
            "{tr}dalle -v",
        ],
        "available pixel size": SIZE,
    },
)
async def dalle_image_generation(event):
    "Generate an Image using the provided text using Openai Api"
    text = event.pattern_match.group(1)
    reply = await event.get_reply_message()
    image_text = "**Available Pixel Size:**\n\n"
    reply_to_id = await reply_id(event)

    # Flag to change pixel size of ai
    if "-s" in text:
        flag = text.replace("-s", "").strip()
        if not flag or flag not in SIZE:
            for index, name in enumerate(SIZE, 1):
                image_text += f"**{index}.** `{name}`\n"
            return await edit_delete(event, image_text, 50)
        addgvar("DALLE_SIZE", flag)
        return await edit_delete(event, f"__Pixel size changed to : **{flag}**__")

    # Flag to change number of output
    elif "-n" in text:
        flag = int(text.replace("-n", "").strip())
        if flag > 0 and flag <= 10:
            addgvar("DALLE_LIMIT", flag)
            return await edit_delete(
                event, f"__Output limit for Dall-E changed to : **{flag}**__"
            )
        return await edit_delete(event, "__Input a value between 1-10.__")

    # Flag to generate a media via editing a media
    elif "-e" or "-v" in text:
        if not reply or not reply.media:
            return await edit_delete(event, "__Reply to a Image with instructions__")
        if "e" in text:
            text = text.replace("-e", "").strip()
            photos, captions = await generate_dalle_image(text, reply, event, "e")
        else:
            photos, captions = await generate_dalle_image(
                "Random Variations", reply, event, "v"
            )

    # If no flag then generate from text
    else:
        photos, captions = await generate_dalle_image(text, reply, event)

    await edit_or_reply(event, "__Uploading...__")
    await event.client.send_file(
        event.chat_id,
        photos,
        caption=captions,
        reply_to=reply_to_id,
        force_document=True,
    )
    await event.delete()
    for i in photos:
        os.remove(i)