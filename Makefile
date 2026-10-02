# Usage:
#   make preview                         # 480p15, all scenes in FILE
#   make preview SCENE=TestScene         # a single scene
#   make final FILE=scenes/foo.py SCENE=Foo
#   make preview ARGS=-p                 # extra manim flags (e.g. open when done)
#   make data                            # re-run data/compute.ipynb -> data/*.json
#   make music                           # Lyria background bed -> media/music/bed.wav (ARGS=--dry-run)

FILE  ?= scenes/test_scene.py
SCENE ?=
ARGS  ?=

MANIM = PYTHONPATH=$(CURDIR):$(CURDIR)/scripts uv run manim
TARGET = $(FILE) $(if $(SCENE),$(SCENE),-a)

.PHONY: preview final data music sync clean

preview:
	$(MANIM) -ql $(ARGS) $(TARGET)

final:
	REQUIRE_ELEVENLABS=1 $(MANIM) -qk --fps 60 $(ARGS) $(TARGET)

data:
	uv run --group data jupyter nbconvert --to notebook --execute --inplace data/compute.ipynb

music:
	uv run --group music python scripts/music.py $(ARGS)

sync:
	uv sync

clean:
	rm -rf media
