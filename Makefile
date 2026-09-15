BOOKING := $(shell sed -n 's/^booking-url: *"\(.*\)"/\1/p' _variables.yml)

.PHONY: qr preview build deploy clean

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
