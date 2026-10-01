from manim import Axes, Create, FadeIn, FadeOut, Text, Write
from manim_voiceover import VoiceoverScene

from style import *
from voice import speech_service


class TestScene(VoiceoverScene):
    def construct(self):
        self.set_speech_service(speech_service())

        title = Text("Machine Learning, visually", font=FONT, font_size=TITLE_SIZE, color=TEXT)
        title.move_to(TITLE_POSITION)

        with self.voiceover(text="Welcome to the course. Let's draw our first function.") as tracker:
            self.play(Write(title), run_time=tracker.duration)

        axes = Axes(x_range=[-3, 3], y_range=[0, 9, 3], x_length=7, y_length=4.5, tips=False)
        axes.set_color(GRID).shift(DOWN * 0.5)
        parabola = axes.plot(lambda x: x**2, color=PRIMARY)

        with self.voiceover(text="Here is a simple parabola, the loss of a one parameter model.") as tracker:
            self.play(FadeIn(axes), Create(parabola), run_time=tracker.duration)

        self.wait(NORMAL)
        self.play(FadeOut(title, axes, parabola), run_time=FAST)
