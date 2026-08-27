# Fast Video Production Package

This is the simplest realistic way to make the demo videos in about one hour.

## Goal

Create a polished, approximately 3-minute product/demo video for the finished Space Biology Evidence Engine using:

- the existing 12-slide pitch deck
- the existing one-page summary
- the real app UI
- the committed screenshots
- a free editor and free recording tools

The fastest path is **not** to generate a continuous AI video. Use mostly:

1. presentation visuals
2. screen recordings
3. subtle zoom/pan on static images
4. a short voiceover
5. royalty-free music

## What to skip

To save time, skip these unless you have extra time at the end:

- AI-generated video clips
- image-to-video animation
- custom motion graphics
- elaborate sound design
- complex transitions
- new slide design
- regenerating the existing PowerPoint decks with Python or any file-generator script

## Source material to use

### Best deck slides

The pitch deck is already a strong video outline.

- Slide 1: title / hook
- Slide 2: research problem
- Slide 3: solution
- Slide 4: architecture credibility
- Slide 5: grounded QA and citations
- Slide 6: controlled corpus and provenance
- Slide 7: search and comparison
- Slide 8: safeguards
- Slide 9: results and quality
- Slide 10: demo readiness and backup plan
- Slide 12: closing / takeaway

Slides 11 can be skipped in the fast version unless you need a short limitations beat.

### Best screenshots

Use the screenshots already committed in `docs/final/screenshots/`:

- `01-home.png`
- `02-ask.png`
- `03-search.png`
- `04-corpus.png`
- `05-compare.png`
- `06-publication.png`

These should be used as full-screen inserts with slow zoom or a simple crop, not as static dead images.

## Fast story

Use this simple narrative:

1. Hook: citation-first research matters because scientific evidence must stay grounded.
2. Problem: space biology evidence is fragmented across papers, models, and terminology.
3. Solution: a controlled corpus of 23 approved papers with provenance-preserving retrieval.
4. Live demo: show Home, Corpus, Search, Ask, Publication, and Compare.
5. Trust: citations, passages, and insufficient-evidence behavior.
6. Close: this helps researchers move from scattered papers to inspectable evidence.

## Easiest production workflow

### Step 1: Record the real app

Record 4 short clips, not one long take.

Recommended length: 10-20 seconds each.

Capture:

- Home
- Corpus
- Search
- Ask
- Compare
- Publication detail

Use simple scrolls, clicks, and one or two example queries.

### Step 2: Build the timeline in a free editor

Assemble the video in this order:

1. Title slide
2. Problem slide
3. Solution slide
4. Screen recording of Home and Corpus
5. Screen recording of Search
6. Screen recording of Ask and citations
7. Screen recording of Compare
8. Screenshot of Publication detail
9. Closing slide

### Step 3: Add narration

Record narration in one pass with a quiet mic setup.

Keep it calm, scientific, and direct.

Target pace: roughly 130-150 words per minute.

### Step 4: Add music very lightly

Keep music low under the voiceover.

Use it mainly at the opening and closing.

### Step 5: Export

Export 1080p, 16:9, H.264 MP4.

## Recommended free / free-tier tools

### 1. Screen recording

**TOOL:** OBS Studio  
**PURPOSE:** Record the real app cleanly.  
**URL:** https://obsproject.com/download  
**FREE ACCESS:** Free and open source.  
**LIMITATION:** None for normal recording use. No watermark.

### 2. Video editing

**TOOL:** DaVinci Resolve  
**PURPOSE:** Assemble the final video, add text, trims, and simple zooms.  
**URL:** https://www.blackmagicdesign.com/products/davinciresolve  
**FREE ACCESS:** Free version available from the official site.  
**LIMITATION:** Studio version is paid; advanced effects are not required for this project.

### 3. Audio recording and cleanup

**TOOL:** Audacity  
**PURPOSE:** Record and clean up narration.  
**URL:** https://www.audacityteam.org/  
**FREE ACCESS:** Free, open source, desktop app.  
**LIMITATION:** None for basic narration editing.

### 4. Royalty-free music and sound effects

**TOOL:** YouTube Audio Library  
**PURPOSE:** Background music and simple sound effects.  
**URL:** https://www.youtube.com/audiolibrary  
**FREE ACCESS:** Free through YouTube Studio.  
**LIMITATION:** Tracks may require attribution depending on license; check each track before use.

### 5. Optional browser-based editor

**TOOL:** CapCut  
**PURPOSE:** Fast alternative if you want an easier editor than Resolve.  
**URL:** https://www.capcut.com/tools/video-editing-software  
**FREE ACCESS:** CapCut advertises a free editor.  
**LIMITATION:** Some features are region-dependent and some AI features may be limited.

## Best use of the deck

If time is short, use the deck as the backbone and do not rebuild it.
Use the existing `.pptx` or exported `.pdf` directly inside the editor, then crop, pan, zoom, or overlay text there.
Do **not** recreate the presentation by generating a new PowerPoint file in Python.

Recommended slide treatment:

- Slide 1: full-screen title with a slow push-in
- Slide 2: crop to the problem statement
- Slide 3: crop to the solution bullets
- Slide 4: zoom to the data flow diagram
- Slide 5: zoom to the evidence-sufficiency section
- Slide 6: full-screen corpus visual if it exists, otherwise use the corpus screenshot
- Slide 7: use the comparison screenshot or deck slide, whichever is clearer
- Slide 8: use as a brief credibility slide
- Slide 9: use as a proof / quality slide
- Slide 10: use as a backup/demo-readiness slide
- Slide 12: closing title card

## Exact one-hour plan

### 0-10 minutes

- open the deck
- open the screenshots
- open the app
- decide the 2 or 3 demo questions

### 10-25 minutes

- record the app clips
- record any narration notes if needed

### 25-40 minutes

- assemble the rough cut
- place deck visuals around the app clips
- add short titles and transitions

### 40-50 minutes

- record or clean narration
- place voiceover on the timeline
- lower music under voice

### 50-60 minutes

- trim the pacing
- add captions or key labels
- export MP4

## Suggested screen-recorded demo flow

### Clip 1: Home

- Start on the home page.
- Show the main navigation and the product positioning.

### Clip 2: Corpus

- Open the corpus.
- Show that the library is controlled and finite.

### Clip 3: Search

- Search for a term that returns a real passage.
- Zoom into the result and the source provenance.

### Clip 4: Ask

- Ask a grounded question.
- Show the answer, citations, and supporting passages.

### Clip 5: Compare

- Show comparison across studies without blending evidence.

### Clip 6: Publication detail

- Open one publication and show source metadata / DOI / provenance.

## Narration strategy

Keep narration simple and calm.

Suggested tone:

- informed
- scientific
- confident
- not salesy

Suggested phrasing pattern:

- problem
- solution
- live proof
- why trust matters
- closing takeaway

## Minimal narration script outline

1. “Space biology evidence is scattered across papers, models, and terminology.”
2. “This application keeps the boundary tight: a controlled corpus of approved publications.”
3. “Search and Ask are grounded in retrieved passages, with citations you can inspect.”
4. “If the evidence is weak, the system says so instead of guessing.”
5. “That makes it useful for researchers who need trustworthy, traceable results.”

## Asset checklist

### Already exists in project

- pitch deck
- one-page summary
- final release document
- app screenshots
- brand assets
- README and demo docs

### Needs screen recording

- Home page
- Corpus page
- Search page
- Ask page
- Compare page
- Publication detail page

### Needs audio

- voiceover narration
- light background music

### Needs editing

- title card
- scene order
- zooms / pans on screenshots
- captions
- final export

### Needs AI generation

- nothing required for the fastest version

## Recommended production decision

For the one-hour version, do **not** spend time on AI video generation. The fastest clean result is:

deck + screenshots + real app recordings + narration + light music + simple edit.

That is the easiest path to a credible final video.
