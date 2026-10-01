# Usage:
#   make preview                         # 480p15, all scenes in FILE
#   make preview SCENE=TestScene         # a single scene
#   make final FILE=scenes/foo.py SCENE=Foo
#   make preview ARGS=-p                 # extra manim flags (e.g. open when done)
#   make data                            # re-run data/compute.ipynb -> data/*.json

FILE  ?= scenes/test_scene.py
SCENE ?=
ARGS  ?=

MANIM = PYTHONPATH=$(CURDIR) uv run manim
TARGET = $(FILE) $(if $(SCENE),$(SCENE),-a)

.PHONY: preview final data sync clean

preview:
	$(MANIM) -ql $(ARGS) $(TARGET)

final:
	REQUIRE_ELEVENLABS=1 $(MANIM) -qk --fps 60 $(ARGS) $(TARGET)

data:
	uv run --group data jupyter nbconvert --to notebook --execute --inplace data/compute.ipynb

sync:
	uv sync

clean:
	rm -rf media
