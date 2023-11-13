import asyncio
from typing import Callable, Union, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message


class MediaCatcher(BaseMiddleware):
    album_data: dict = {}
    
    def __init__(self, latency: Union[int, float] = 0.2):
        self.latency = latency
    
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        if not event.media_group_id:
            await handler(event, data)
            return
        try:
            self.album_data[event.media_group_id].append(event)
        except KeyError:
            self.album_data[event.media_group_id] = [event]
            await asyncio.sleep(self.latency)
            
            data['_is_last'] = True
            data["album"] = self.album_data[event.media_group_id]
            await handler(event, data)
        
        if event.media_group_id and data.get("_is_last"):
            del self.album_data[event.media_group_id]
            del data['_is_last']
