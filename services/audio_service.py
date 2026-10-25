import edge_tts


class AudioService:
    async def stream_audio(self, text:str):
        
        voice = "pt-PT-RaquelNeural"
        
        comm = edge_tts.Communicate(text, voice)
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                yield chunk["data"]
    

        