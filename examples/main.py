from dunite import Server, Context

app = Server(__name__)


@app.on("PlayerMessage")
async def on_message(ctx: Context):
    print(ctx)
    return


app.run()
