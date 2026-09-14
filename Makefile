BOOKING := $(shell sed -n 's/^booking-url: *"\(.*\)"/\1/p' _variables.yml)

.PHONY: qr preview build deploy clean

## regenerate the office-hours QR code from booking-url in _variables.yml
qr:
	qrencode -t SVG -o images/qr-office-hours.svg -s 8 -m 2 -l M "$(BOOKING)"
	@echo "QR -> $(BOOKING)"

preview:
	quarto preview

build: qr
	quarto render

deploy: build
	netlify deploy --prod --dir=_site

clean:
	rm -rf _site .quarto
