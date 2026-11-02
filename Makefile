BOOKING := $(shell sed -n 's/^booking-url: *"\(.*\)"/\1/p' _variables.yml)

.PHONY: qr preview build deploy clean clips

## regenerate the office-hours QR code from booking-url in _variables.yml
qr:
	qrencode -t SVG -o images/qr-office-hours.svg -s 8 -m 2 -l M "$(BOOKING)"
	@echo "QR -> $(BOOKING)"

preview:
	quarto preview

# `qr` is intentionally not a prerequisite: the booking page carries the link
# itself, so a build no longer depends on a live booking-url. Run `make qr` by
# hand if a printable code is ever needed.
build:
	quarto render

deploy: build
	netlify deploy --prod --dir=_site

clean:
	rm -rf _site .quarto

## render every manim scene at deck quality, remux moov-first, copy where the site serves them
# scenes.py holds the helpers, lecture 11 and the Module 1 lab; lectures 12, 14, 18
# and 19 have a file each, which imports scenes.py. One group per file.
SCENES_11 := Lloyd KmeansByHand ScaleBreaks ShapeBreaks ElbowLie Silhouette
SCENES_LAB := TwoMeans LeastSquares LogitCurve ShrinkPath Decompose
SCENES_scenes := $(SCENES_11) $(SCENES_LAB)
SCENES_scenes_12 := Dendrogram LinkageFour DendrogramRead
SCENES_scenes_14 := Rotation PCAByHand ScreeChoice
SCENES_scenes_18a := Boundary PerceptronByHand Perceptron GradientDescent
SCENES_scenes_18b := Sigmoid HiddenLayer Overfitting
SCENES_scenes_19 := DataSplit ValidationCurve ModelRace DeepScale AutoencoderPCA
CLIP_FILES := scenes scenes_12 scenes_14 scenes_18a scenes_18b scenes_19
MEDIA := $(HOME)/.cache/sbd-manim-media/videos
clips:
	mkdir -p lectures/media
	$(foreach f,$(CLIP_FILES),(cd animations && .venv/bin/manim -qm --disable_caching $(f).py $(SCENES_$(f))) && \
	  for s in $(SCENES_$(f)); do ffmpeg -v error -y -i $(MEDIA)/$(f)/720p30/$$s.mp4 -c copy -movflags +faststart lectures/media/$$s.mp4; done;)

## quick, low-quality render of every scene: for checking frames, not for the deck
clips-preview:
	$(foreach f,$(CLIP_FILES),(cd animations && .venv/bin/manim -ql --disable_caching $(f).py $(SCENES_$(f)));)
