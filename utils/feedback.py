from contextlib import asynccontextmanager
import discord


class _FeedbackHandle:
    def __init__(self, msg):
        self._msg = msg

    async def update(self, content: str):
        if not self._msg:
            return
        try:
            await self._msg.edit(content=content)
        except discord.HTTPException:
            pass


@asynccontextmanager
async def processing_feedback(ctx, content: str):
    """Envia uma mensagem temporária de feedback no chat e a remove ao finalizar."""
    msg = None
    try:
        msg = await ctx.send(content)
    except discord.HTTPException:
        pass

    handle = _FeedbackHandle(msg)
    try:
        yield handle
    finally:
        if msg:
            try:
                await msg.delete()
            except discord.HTTPException:
                pass
