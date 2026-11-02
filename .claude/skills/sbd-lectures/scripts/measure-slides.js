// Paste into the browser's javascript tool on a deck in _site (tab at 1280x720).
// For every slide, how far down its content reaches, in slide pixels. The footer
// starts at about 697, so anything above LIMIT is overprinted or off the slide.
const LIMIT = 680;
const slides = Reveal.getSlides();
const over = [];
for (let i = 0; i < slides.length; i++) {
  Reveal.slide(i);
  await new Promise(r => setTimeout(r, 70));
  const s = slides[i];
  const top = s.getBoundingClientRect().top;
  const scale = Reveal.getScale();
  let bottom = 0;
  s.querySelectorAll('*').forEach(e => {
    const r = e.getBoundingClientRect();
    if (r.height) bottom = Math.max(bottom, (r.bottom - top) / scale);
  });
  if (bottom > LIMIT) {
    const title = s.querySelector('h2')?.textContent.trim().slice(0, 40) || s.id;
    over.push(`${i} ${title}: ${Math.round(bottom)}`);
  }
}
`${slides.length} slides; over ${LIMIT}px: ` + (over.join(' | ') || 'none');
