# Optima Store → Bosfor Anatolya — Christmas card video: prompt pack (Version 3)

Roles: **Optima Store is the sender; Bosfor Anatolya is the recipient (a client of Optima).** The card is from Optima to Bosfor, so the message addresses Bosfor, the sign-off is Optima, and the envelope is addressed to Bosfor Anatolya.

Use this in any image + video model (Kling, Veo, Sora, Runway). Prompts are in English because the models follow English best; every on-card word stays in Romanian, quoted exactly.

How the pieces fit: generate the card artwork first (Part 1), then use those images as references for the video prompt (Parts 2 and 3). Add the real logo, the real text and the end card in an editor afterwards. Video models cannot be trusted with small lettering or a logo, so they never get the final say on either.

---

## Part 1 — Prompt to generate the Christmas card

### 1A. Front cover (artwork only, recommended)

```
Elegant watercolor Christmas card front, portrait 3:4. A delicate border of snow-dusted pine branches, small red berries and tiny white snowflakes with a few gold flecks around all four edges. The large centre area is empty cream-white cold-press paper. Palette strictly steel blue (#4E6DA4), deep red (#A02B21), cream white, a little gold. Refined, airy, corporate-friendly, no people. No text, no letters, no numbers, no logos anywhere.
```

Add the words on top afterwards: "Crăciun Fericit!" in red cursive (#A02B21), with the two logos side by side near the bottom on small round labels, joined by a gold arrow that points from sender to recipient: the Optima Store logo (white label, sender) on the left and the Bosfor Anatolya logo (green label, recipient) on the right. This keeps the diacritics (ă) correct. This is how the card was made in Version 1 and Version 2.

### 1B. Front cover with the text drawn by the model (only if you want to try it)

```
Same watercolor Christmas card front as above, and in the empty centre write in elegant red connected cursive calligraphy, on two lines, exactly: "Crăciun" / "Fericit!". The letter "ă" must have the breve mark exactly as in Romanian. No other text.
```

Check the result letter by letter. If a character is wrong, use 1A.

### 1C. Inside right page (handwritten message)

```
The inside right page of a greeting card, portrait 3:4, warm ivory paper with a thin steel-blue double border and a tiny blue snowflake in each corner. Handwritten with a fountain pen in dark navy ink (#1B2442), in elegant connected cursive, slightly slanted to the right, natural pressure variation, a slightly uneven baseline, each line very slightly different, exactly this Romanian text on separate lines:

Dragă echipă Bosfor Anatolya,
vă mulțumim pentru încrederea
pe care ne-ați acordat-o
în acest an.
Vă dorim un Crăciun liniștit,
plin de lumină și bucurie,
și un An Nou cu sănătate
și realizări!
Cu drag,
Echipa Optima Store

Keep the diacritics exactly: ă, â, î, ș, ț. No extra words.
```

### 1D. Inside left page

```
The inside left page of a greeting card, portrait 3:4: deep blue (#3B5688) with a soft vertical gradient and delicate white snowflakes, one round white label in the centre. (Place the real Optima Store logo on the label in an editor; Optima is the sender.) Small white text at the bottom: "optimastore.ro".
```

---

## Part 2 — Cursive writing (include this block in the video prompt)

```
HANDWRITING: elegant connected cursive calligraphy written with a fountain pen, dark navy ink, slanted about 12 degrees to the right. It must look like a real person writing: each word forms stroke by stroke from left to right, letters join, i-dots and t-bars come after the word, small pauses between lines, the pen nib visible at the leading edge of the ink and following the lines of text. Not a typed font, not fading in all at once, never changing a letter once written. Text, in Romanian, exactly as in the reference image, top to bottom.
```

---

## Part 3 — Transition prompt: handed over, drawn out, opened, written, closed, put back

### 3A. One continuous shot (12 seconds, 9:16)

```
Vertical 9:16, 12 seconds, 24 fps, cinematic, soft warm light, shallow depth of field. Winter evening, warm out-of-focus string lights and gently falling snow in the background.

0.0–1.5 s: Point-of-view. From the receiver's (Bosfor Anatolya's) point of view, a person's hand in a dark navy coat sleeve (no face visible, natural hand with five fingers) holds out a steel-blue envelope with a white round Optima Store label on its pointed flap and a cream address label reading "Pentru Bosfor Anatolya" (logos and address lettering are checked or added in post), and hands it to the camera. The envelope moves into the centre of the frame and settles in the viewer's two hands.
1.5–3.0 s: A thumb lifts the pointed flap; the flap folds back and the inside lining shows. A greeting card begins to slide up out of the envelope.
3.0–4.5 s: The card comes out fully and faces the camera: cream watercolor cover with snow-dusted pine branches, red berries and the red cursive words "Crăciun Fericit!".
4.5–6.0 s: The card opens like a book (spine on the left). Left page deep blue with white snowflakes and the Optima Store label (sender); right page warm ivory paper addressed to Bosfor Anatolya.
6.0–8.5 s: Slow push-in on the right page. The handwritten message is written live in dark navy fountain-pen ink as described in the HANDWRITING block above. A gentle sparkle at the pen tip.
8.5–9.5 s: Hold, the message fully readable and still. Very slow push-in.
9.5–10.5 s: The right page swings back, the card closes with the cover facing the camera.
10.5–12.0 s: The card slides back down into the envelope, the flap folds closed over it, and the envelope is held out and gently taken away, ending exactly like the first frame.

Camera: stable, slight handheld drift, no cuts. Mood: warm, sincere, professional thank-you. Palette: steel blue #4E6DA4, deep red #A02B21, cream, gold.
```

### 3B. If your model only allows 5 to 10 seconds, split it into three clips and join them

Make each clip start from the last frame of the previous one (use the "start frame" option).

1. Clip 1, 0–4.5 s: hand-over, flap opens, card slides out, cover facing the camera.
2. Clip 2, 4.5–9.5 s: opens, handwriting is written, hold.
3. Clip 3, 9.5–12 s: closes, slides back into the envelope, flap closes, envelope taken away (use the very first frame as the end frame so it loops).

### 3C. Negative prompt

```
no face, no extra fingers, no deformed hands, no text other than the card text, no watermark, no subtitles, no brand logos other than the Optima Store label, no invented logos, no changes of spelling, no morphing letters, no flicker, no jump cuts, no sudden camera shake, no cartoon style
```

---

## Part 4 — What you were missing (added)

1. **Text and logo safety.** AI video distorts small lettering and logos. Give the video model the card images as references, then replace the card text and the logo in an editor, or accept the video only for the motion and overlay the real writing.
2. **Start and end frame.** For "closes and goes back into the envelope", use the closed envelope as both the first and the last frame so the clip loops cleanly. Kling and Veo both support first/last frames.
3. **Format.** 9:16 for Reels and Stories at 1080×1920. Keep the important action out of the top 14% and bottom 20% where the app buttons sit.
4. **Length.** 10 to 12 seconds total. Most models cap one clip at 5 to 10 seconds, hence 3B.
5. **Consistency.** Use the same reference images (card front, inside, envelope, logo) in every clip, and a fixed seed if the model offers one.
6. **Hands.** If hands look wrong, replace the hand with an envelope sliding in from the side, or a gloved hand.
7. **Sound.** Soft music, paper rustle when the flap opens, a faint pen-scratch while writing. Record or add it separately, as models often skip it. No copyrighted music.
8. **End card.** Add "Crăciun fericit!", both logos (Optima Store on the left, a gold arrow, Bosfor Anatolya on the right), "Cu drag, Optima Store" and "optimastore.ro" as a 2 second overlay at the end, made in an editor.
9. **AI disclosure.** If you post a generated video, mark it as AI-generated where the platform asks.
10. **Language check.** Have a Romanian speaker read the final text once. A single wrong diacritic on a client greeting looks careless.
11. **Open questions.** Has Optima Store approved the card text (it speaks for Optima to Bosfor Anatolya), and is the contact person at Bosfor Anatolya known by name so the salutation can be personal? Are higher-resolution logos available (the Optima file is 447 px and the Bosfor one 554 px)? Is the logo arrangement fine with both brands?
12. **Rights.** Before paid use, check three things: the commercial-use terms of your Kling plan for the cover artwork, the font licence (the handwriting font in Versions 1 and 2 is TeX Gyre Chorus, which ships with a free-use licence, but confirm it), and replace the synthesized music with licensed music.
