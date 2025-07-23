import asyncio

import numpy as np
import numpy.typing as npt
import sounddevice as sd
import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets

from agents import Agent, Runner, function_tool, SQLiteSession
from openai import AsyncOpenAI

# ── Robot‑specific modules ─────────────────────────────────────────── #
# from Utils.RoboticPathMovement.robotConfig import RoboticArm
from Utils.AgenticTools.assistantTools import (
    generate_drawing,
    edit_drawing,
    capture_image,
    draw_image,
)
from Utils.UserInput.inputController import receiveInput  # blocking; returns str

# ── OpenAI client ──────────────────────────────────────────────────── #
openai_async = AsyncOpenAI()  # gets key from env

# ── Global pyqtgraph style ────────────────────────────────────────── #
pg.setConfigOption("background", "#101010")  # deep charcoal
pg.setConfigOption("foreground", "#CCCCCC")  # soft grey text

# ── Audio waveform visualiser (smooth, scrolling R→L) ────────────── #
class AudioVisualizer:
    """Smooth scrolling oscilloscope (~300 ms history)."""

    def __init__(
        self,
        samplerate: int = 24_000,
        history_ms: int = 300,
        kernel: int = 7,  # moving‑average window (odd)
    ) -> None:
        self.samplerate = samplerate
        self.buf_len = int(samplerate * history_ms / 1_000)
        self.data = np.zeros(self.buf_len, dtype=np.float32)

        # smoothing kernel
        self._kernel = np.ones(kernel, dtype=np.float32) / kernel

        # single QApplication
        pg.mkQApp()

        # window
        self.win = pg.GraphicsLayoutWidget(show=True, title="TTS Waveform")
        self.win.resize(600, 240)
        self.win.setWindowTitle("TTS Waveform")

        self.plot = self.win.addPlot()
        self.plot.hideAxis("left")
        self.plot.hideAxis("bottom")
        self.plot.setMouseEnabled(False, False)
        self.plot.setYRange(-1, 1, padding=0)

        self.curve = self.plot.plot(pen=pg.mkPen("#1E90FF", width=2))

    def _smooth(self, arr: npt.NDArray[np.float32]) -> npt.NDArray[np.float32]:
        return np.convolve(arr, self._kernel, mode="same")

    def add_samples(self, pcm: npt.NDArray[np.int16]) -> None:
        """Append new samples, update scrolling plot."""
        samples = pcm.astype(np.float32) / 32768.0
        if samples.ndim > 1:
            samples = samples[:, 0]

        n = samples.size
        if n >= self.buf_len:
            self.data[:] = samples[-self.buf_len :]
        else:
            # shift left, append new at end → scroll R→L visually
            self.data = np.roll(self.data, -n)
            self.data[-n:] = samples

        smoothed = self._smooth(self.data)
        self.curve.setData(smoothed)
        QtWidgets.QApplication.processEvents()


# ── Custom, low‑latency audio player ──────────────────────────────── #
class AudioPlayer:
    """Streams PCM chunks from the OpenAI TTS endpoint to the sound card."""

    def __init__(
        self,
        blocksize: int = 1024,
        latency: str | float | None = "low",
        samplerate: int = 24_000,
        visualizer: "AudioVisualizer | None" = None,
    ) -> None:
        self.blocksize = blocksize
        self.latency = latency
        self.samplerate = samplerate
        self.visualizer = visualizer

    async def play(self, response) -> None:
        with sd.OutputStream(
            samplerate=self.samplerate,
            channels=1,
            dtype=np.int16,
            blocksize=self.blocksize,
            latency=self.latency,
        ) as stream:
            async for chunk in response.iter_bytes(chunk_size=self.blocksize * 2):
                pcm = np.frombuffer(chunk, dtype=np.int16)

                if self.visualizer:
                    self.visualizer.add_samples(pcm)

                stream.write(pcm)

            stream.write(np.zeros(self.samplerate, dtype=np.int16))


# ── Tool wrappers (robot‑specific) ─────────────────────────────────── #


@function_tool(strict_mode=True)
def generate_image(image_prompt: str) -> str:
    print(f"Generating image with prompt: {image_prompt}")
    # return generate_drawing(image_prompt, robotic_arm)


@function_tool(strict_mode=True)
def edit_image(edit_prompt: str) -> str:
    print(f"Editing image with prompt: {edit_prompt}")
    # return edit_drawing(edit_prompt, robotic_arm)


@function_tool
def capture_drawing() -> str:
    print("Capturing current drawing from the canvas.")
    # return capture_image()


# ── Agent definition ──────────────────────────────────────────────── #
CREATIVE_PROMPT = """
As a creative robotic assistant, you have a 6‑axis arm and are equipped with a marker. Your role is to work collaboratively with human artists by assisting in artistic creation and encouraging creativity. This involves brainstorming novel artistic ideas, generating new images to draw, and editing existing images to illustrate new edits.
Your only purpose is as a creative assistant. You should not provide assistance to questions which don’t relate to assisting the user’s creative and drawing process.

# Tasks

1. **Workshopping Ideas**:
   – Engage with the user to explore creative concepts.
   – Ask probing questions to refine and expand on these concepts.

2. **Generating Images**:
   – Create novel images based on discussed concepts.
   – Ensure the generated images align with the user's desired style and theme.

3. **Editing Images**:
   – Make precise edits and stylistic changes to existing images already drawn on the canvas as per user feedback.

# Output Format
Responses should be provided in natural language, with clear instructions for the user. When generating or editing images, provide a brief description of the changes made or the concept illustrated. Always confirm with the user before executing any drawing or editing tasks.
The robot draws using a single coloured chalk marker on an acrylic sheet. It is limited to a single colour and details available using a 5 mm marker.

# Personality

Act as a kind, charming and helpful artistic assistant. Be inquisitive and creative, always seeking to understand the user's artistic vision. Use a positive and encouraging tone, fostering a collaborative atmosphere. Your goal is to enhance the user's creative process and produce visually appealing artwork together.

# Tools

The following tools are available to you:

* `generate_image(user_prompt)`: Generates an image via OpenAI’s image API, decomposes it into line vectors and draws it on the canvas using the robotic arm. Use only when the canvas is blank.
* `edit_image(user_prompt)`: Captures a photo of the current canvas state, sends the image plus prompt to OpenAI’s image‑editing API, erases the existing drawing and draws the new version.
* `capture_drawing()`: Captures a photo of the current canvas and returns a description of what is depicted.

# Notes

– Always check in with the user for feedback on generated outputs.
– If unsure of the canvas state, call `capture_drawing`.
– Remain flexible to evolving user preferences and ideas.
"""

creative_agent = Agent(
    name="Creative Drawing Robot",
    instructions=CREATIVE_PROMPT,
    model="gpt-4o",
    tools=[generate_image, edit_image, capture_drawing],
)


_visualizer: "AudioVisualizer | None" = None  # shared singleton

# ── TTS helper ────────────────────────────────────────────────────── #
async def speak(text: str, voice: str = "alloy") -> None:
    global _visualizer
    if _visualizer is None:
        _visualizer = AudioVisualizer()

    async with openai_async.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice=voice,
        input=text,
        instructions="Speak in a cheerful and positive tone.",
        response_format="pcm",  # 24 kHz mono 16‑bit LE
    ) as resp:
        await AudioPlayer(visualizer=_visualizer).play(resp)


# ── Main event loop ───────────────────────────────────────────────── #
async def main() -> None:
    from pyfiglet import Figlet

    print(Figlet(font="slant").renderText("Robot Creative Assistant"))
    print("Speak or type your idea – I’ll answer out loud!\n")

    while True:
        try:
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