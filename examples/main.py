from dunite import Server, Context
from dunite.types.commands import CommandResponse
from dunite.types.events import EventType

app = Server(__name__)


@app.on(EventType.START_CLIENT)
async def start_client(ctx: Context):
    print(ctx)
    return


@app.on(EventType.PLAYER_MESSAGE)
async def on_message(ctx: Context):
    print(ctx)
    res: CommandResponse = await ctx.run_command("title @a actionbar hey!")
    print(res)
    return


app.run()
