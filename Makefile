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
# lecture 11 ------------------------------------------------------------------
SCENES_11 := Lloyd KmeansByHand ScaleBreaks ShapeBreaks ElbowLie
# lecture 12 ------------------------------------------------------------------
SCENES_12 := Dendrogram LinkageFour DendrogramRead
# lecture 18 ------------------------------------------------------------------
SCENES_18 := Boundary PerceptronByHand Perceptron GradientDescent Sigmoid HiddenLayer Overfitting
# lecture 19 (the lab) ---------------------------------------------------------
SCENES_19 := DataSplit ValidationCurve ModelRace DeepScale AutoencoderPCA
SCENES := $(SCENES_11) $(SCENES_12) $(SCENES_18) $(SCENES_19)
clips:
	cd animations && .venv/bin/manim -qm --disable_caching scenes.py $(SCENES)
	mkdir -p lectures/media
	for s in $(SCENES); do \
	  ffmpeg -v error -y -i $(HOME)/.cache/sbd-manim-media/videos/scenes/720p30/$$s.mp4 -c copy -movflags +faststart lectures/media/$$s.mp4; \
	done

## quick, low-quality render of every scene: for checking frames, not for the deck
clips-preview:
	cd animations && .venv/bin/manim -ql --disable_caching scenes.py $(SCENES)
