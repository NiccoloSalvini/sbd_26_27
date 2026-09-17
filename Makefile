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

## render every manim scene at deck quality and copy the clips where the site serves them
clips:
	cd animations && uv run manim -qm --disable_caching scenes.py LearningRate Overfitting
	mkdir -p lectures/media
	cp animations/media/videos/scenes/720p30/LearningRate.mp4 lectures/media/gd-learning-rate.mp4
	cp animations/media/videos/scenes/720p30/Overfitting.mp4  lectures/media/overfitting.mp4
