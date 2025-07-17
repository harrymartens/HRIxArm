"""
Creative Drawing Robot — async voice version with custom AudioPlayer
-------------------------------------------------------------------
* Requires OPENAI_API_KEY in your environment.
* Tested on Python 3.10–3.12, macOS & Linux.
"""

import asyncio
from agents import Agent, Runner, function_tool, SQLiteSession
from openai import AsyncOpenAI
import numpy as np
import numpy.typing as npt
import sounddevice as sd

# ── Robot-specific modules ─────────────────────────────────────────── #
from Utils.RoboticPathMovement.robotConfig import RoboticArm
from Utils.AgenticTools.assistantTools import (
    generate_drawing,
    edit_drawing,
    capture_image,
    draw_image,
)
from Utils.UserInput.inputController import receiveInput   # blocking; returns str

openai_async = AsyncOpenAI()  # gets key from env

# ── Custom, tunable audio player ───────────────────────────────────── #
class AudioPlayer:
    """
    Low-latency 24 kHz mono PCM playback using sounddevice.

    Parameters
    ----------
    blocksize : int
        Number of frames per PortAudio callback. Larger => more latency,
        smaller => higher underrun risk.
    latency :  str | float | None
        Forwarded to sounddevice (can be "low", "high" or seconds).
    samplerate : int
        Must match the TTS sample rate.
    """
    def __init__(
        self,
        blocksize: int = 4096,
        latency: str | float | None = "high",
        samplerate: int = 24_000,
    ) -> None:
        self.blocksize = blocksize
        self.latency = latency
        self.samplerate = samplerate

    async def play(self, response) -> None:
        """Stream bytes from a TTS streaming response to the audio device."""
        with sd.OutputStream(
            samplerate=self.samplerate,
            channels=1,
            dtype=np.int16,
            blocksize=self.blocksize,
            latency=self.latency,
        ) as stream:
            async for chunk in response.iter_bytes(chunk_size=8192):
                pcm: npt.NDArray[np.int16] = np.frombuffer(chunk, dtype=np.int16)
                stream.write(pcm)

            # One second of silence so the tail isn’t clipped
            stream.write(np.zeros(self.samplerate, dtype=np.int16))

# ── Tool wrappers ──────────────────────────────────────────────────── #
robotic_arm = RoboticArm()

@function_tool(strict_mode=True)
def generate_image(image_prompt: str) -> str:
    return generate_drawing(image_prompt, robotic_arm)

@function_tool(strict_mode=True)
def edit_image(edit_prompt: str) -> str:
    return edit_drawing(edit_prompt, robotic_arm)

@function_tool
def capture_drawing() -> str:
    return capture_image()

@function_tool
def draw_last_generated_image() -> str:
    return draw_image(robotic_arm)

# ── Agent definition ───────────────────────────────────────────────── #
CREATIVE_PROMPT = """
As a creative robotic assistant you have a 6-axis arm and a single 5 mm chalk
marker. Brainstorm ideas, generate sketches, and edit drawings. If unsure what
is on the canvas, call `capture_drawing`. Keep replies under 100 words and
focus solely on artistic tasks.
"""

creative_agent = Agent(
    name="Creative Drawing Robot",
    instructions=CREATIVE_PROMPT,
    model="gpt-4o",
    tools=[
        generate_image,
        edit_image,
        capture_drawing,
        draw_last_generated_image,
    ],
)

# ── TTS helper using the custom player ─────────────────────────────── #
async def speak(text: str, voice: str = "alloy") -> None:
    """
    Stream TTS through our AudioPlayer.
    """
    async with openai_async.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice=voice,
        input=text,
        instructions="Speak in a cheerful and positive tone.",
        response_format="pcm",      # 24 kHz 16-bit LE mono
    ) as resp:
        await AudioPlayer(blocksize=4096, latency="high").play(resp)

# ── Main event loop ────────────────────────────────────────────────── #
async def main() -> None:
    from pyfiglet import Figlet
    print(Figlet(font="slant").renderText("Robot Creative Assistant"))
    print("Speak or type your idea – I’ll answer out loud!\n")


    while True:
        try:
            # run blocking input in background thread to keep loop responsive
            user_text = await asyncio.to_thread(receiveInput, "You: ")
            if user_text.strip().lower() in {"exit", "quit"}:
                break

            result = await Runner.run(creative_agent, user_text)
            reply = result.final_output
            print(f"\nRobot:\n{reply}\n")
            await speak(reply)

        except KeyboardInterrupt:
            break

    print("\nConversation ended. Goodbye!")

if __name__ == "__main__":
    asyncio.run(main())
