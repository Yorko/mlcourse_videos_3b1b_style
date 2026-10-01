# Final editing in iMovie

The same workflow works in iMovie 10 on the Mac. The main difference is that iMovie can't measure or normalize loudness, so step 2 happens outside it with ffmpeg (already installed for Manim). Menu names below are from iMovie 10.x; recent versions may differ slightly.

**1. Assemble, music, sound effects**

Create a project with File > New Movie. Before adding anything, open Settings at the top right of the timeline and turn off automatic content, so iMovie doesn't insert its own transitions and titles. In the same panel, turn on Show Waveforms; you'll need them to line up sound effects.

Import the ten scene files with File > Import Media. They're in `media/videos/sXX_*/<quality>/`. Use the files from a final render (`-qk --fps 60`), because the first clip you add sets the project's resolution and frame rate. Drag the scenes onto the timeline in order.

For pauses between sections, use a freeze frame rather than a black clip. Each scene ends on the empty dark background (`#111318`), and iMovie's black background is pure black, so you'd see a faint flash. Put the playhead on the last frame of a scene, choose Modify > Add Freeze Frame (Option-F), and drag its edge to about 0.5–1 s.

Background music: drag your Epidemic Sound or Artlist track into the music well at the bottom of the timeline (the note icon). Background music there stays put when you rearrange clips. iMovie also comes with free soundtracks under Audio & Video > Soundtracks, if you want to try those first.
- Turn the music down: select it, then drag the volume line on the clip down or use the Volume button above the viewer. Start around 10–20%.
- Duck it under the voice: the narration lives inside your scene clips, so select all the video clips (click one, then Cmd-A), click Volume, and tick "Lower volume of other clips". Start at 20–30% and adjust by ear.
- Drag the fade handles at the music's ends to fade in at the start and out over the title card.

Sound effects: iMovie has a built-in library under Audio & Video > Sound Effects. Drag an effect to the exact frame of a split or highlight; it attaches to the video clip above it. Zoom in with Cmd-= to place it accurately. Keep them quiet, around 30–50% volume, and use them sparingly.

There's a more precise alternative: put the sound effects in Manim itself with `self.add_sound("sfx/pop.wav")` at the moment a cut appears. They then stay frame-accurate even after you re-render a scene. In iMovie, every re-render means re-aligning by hand. I can add that to the scenes if you like.

**2. Mastering to −14 LUFS**

Export first with File > Share > File, choosing 4K and Best (ProRes) or High quality, for example as `final.mp4`. Then normalize in two passes in Terminal.

Measure:

```bash
ffmpeg -i final.mp4 -af loudnorm=I=-14:TP=-1:LRA=11:print_format=json -f null - 2>&1 | tail -12
```

Then apply, copying the four measured values from that output:

```bash
ffmpeg -i final.mp4 -c:v copy -c:a aac -b:a 192k -ar 48000 \
  -af loudnorm=I=-14:TP=-1:LRA=11:measured_I=X:measured_TP=X:measured_LRA=X:measured_thresh=X:linear=true \
  final_yt.mp4
```

This normalizes the whole mix to −14 LUFS integrated with peaks below −1 dBTP. The video isn't re-encoded, so there's no quality loss. If you'd prefer a GUI, Audacity's Loudness Normalization effect does the same, but then you have to put the audio back with the video yourself.

iMovie can't import the `.srt` subtitles. Upload `out/decision_trees.srt` to YouTube separately, which is better anyway because viewers can switch captions on and off.

**3. Review**

Watch `final_yt.mp4` in QuickTime, full screen, rather than in iMovie's preview. That way you're checking the actual normalized file. Watch it once at 1× with good headphones, listening for music fighting the voice, sound effects that are too loud, and pauses that drag.

Then watch it again muted. Check that each section's main object (the jar, the cut, the bars, the boxes) is obvious without the voice. Check that the colors keep their meaning, and that there's never a stretch where nothing moves. Whatever confuses you with the sound off is where a label or a highlight would help.
