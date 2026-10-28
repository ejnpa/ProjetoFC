import edge_tts


class AudioService:
    
    voice = "pt-PT-RaquelNeural"
    
    async def stream_audio(self, text:str):
        
        comm = edge_tts.Communicate(text, self.voice)
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                yield chunk["data"]
    
    
    async def synthesize(self, text: str) -> bytes:
        chunks: list[bytes] = []
        async for chunk in self.stream_audio(text):
            chunk.append(chunk)
        return b"".join(chunks)    
            

        