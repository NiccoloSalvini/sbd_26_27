# Announcement — software setup, before the first lab

Posted to the 26/27 course (`_170037_1`). Body is BBML: `p`, `ul`, `li`,
`a[href]`, `strong`, `br` — no `<b>`, no `<i>`.

**Title:** Install R before the first lab — one line, and a lab session being arranged

**Body (BBML):**

```html
<p>Dear all,</p>

<p>Two things about the software we will use.</p>

<p><strong>First, we are arranging an early lab session.</strong> I am agreeing a slot with the administration and expect to have a date by the end of this week. That session is where we set everything up together and sort out whatever has gone wrong on individual machines, so if you hit trouble, it is not a problem you have to solve alone.</p>

<p><strong>Second, in the meantime, most of it installs itself.</strong> Go to <a href="https://sbd-26-27.netlify.app/setup.html">the Setup page</a> and follow the three steps: install R, install RStudio, then paste one line into the RStudio console. That line checks your R version, installs the packages this course uses, creates a project folder, and finishes by telling you in plain words what it did. It needs no terminal, and running it twice is harmless, so there is no way to get it wrong by trying again.</p>

<p>It has been tested on Windows and on macOS, on a current R and on an older one, and on Linux. It should behave.</p>

<p><strong>If it does not, stop after twenty minutes.</strong> That is not a failure on your part: a locked-down laptop, a corporate antivirus or an R installation from three years ago can each block it, and none of them is worth an evening. Two things to do instead:</p>

<ul>
<li>Bring it to the lab session. That is what it is for.</li>
<li>Or use <a href="https://posit.cloud">Posit Cloud</a>, which is RStudio in a browser tab and installs nothing. The same pasted line works there, and the Setup page explains it.</li>
</ul>

<p>Either way, write to me with the exact error text if you get one. Knowing which machines fail before the lab is what lets me make that session useful rather than improvised.</p>

<p>There is nothing to hand in and nothing here is graded. It only means that when we meet in the lab we spend the time on statistics instead of on installers.</p>

<p>Best,<br>Niccolo Salvini</p>
```

## Notes on the claims in it

- "tested on Windows and on macOS, on a current R and on an older one, and on
  Linux" rests on the CI run of 22 September 2026: `windows-latest` on R release
  and on 4.4.1, `macos-latest` on R release, `ubuntu-latest` with a binary
  mirror. All four green.
- Linux without a binary mirror compiles for an hour and can fail. The script
  detects that case and warns before starting.
- The twenty-minute limit and Posit Cloud are also on the Setup page; the
  announcement repeats them because nobody reads to the bottom of a page they
  are already annoyed with.
