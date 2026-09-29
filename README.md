# PreFlight,  Pre-release Metadata Risk Detector
# Video Demo: (https://youtu.be/1spiNVe0LCQ)
# Author: Riccardo Durante
# City, country: Rome, Italy
# Date: 25 August 2026

# Main Description

I created "PreFlight" for my final CS50 project just because I wanted to 
work on something related to music technology (my field of studies).
I was reading about the same thing while searching for a concrete problem
to address: the "black box" of unpaid royalties for artists then decided 
to start.
 
This money sits in a account managed by streaming platforms and  
societies, waiting for an artist/musician the system can not identify. 
Every year, hundreds of millions of dollars in music royalties are never 
paid to the artists/musician who earned them. The U.S. Mechanical 
Licensing Collective reported $424 million in unclaimed mechanical 
royalties in 2021. The real creators never see it, 
just because after a few years, most of the money is redistributed to the 
largest rights holders based on market share.

It's not a fraud: what surprised me most is the reason for it all. 
A missing code, a typo in the author's name, an incorrect distribution 
percentage: it's incorrect metadata. And it's a economic loss for 
musicians and artists, because small errors like these can compromise the 
entire payment cycle.

My idea for the project became clear once I understood this. This is slow 
and often ineffective, given that most existing tools try to "recover" the 
money after it's already been lost. I wanted to try the opposite: checking 
the metadata "before" publication, when correcting a code or name doesn't 
cost anything yet.
It does exactly that: PreFlight is a small web app that runs seven 
validation rules on the song's metadata after the user fills out a form 
and returns a risk score from 0 to 100. What's wrong, why it's causing 
revenue loss, and how to fix it: for each problem, the report shows all of 
this. The report can also be downloaded as a PDF.

This isn't a finished product; it's just like a proof of concept. I think 
the idea itself is sound, and building it taught me a lot. 
I will work on improving it.

# Files list

# app.py
this app has six paths: it starts the home page with the module."About" page 
explains the idea, "analyze" processes the module, "/report/<id>" 
displays the result, "/report/<id>/pdf" returns the PDF, and 
"/history" with the list of analyzed traces. The Flask application is 
organized like this.

# checks.py
This is the part where I spent most of my time, and it is the heart 
of the project. Each rule is a small function that recovers the trace 
data and returns a "severity, message, solution" dictionary if it finds 
a problem, or "None" if everything is OK. The file contains the 7 
validation rules. At the end of the file, a small function converts the 
list of issues into a risk score (To implement better later based on what 
is needed).

# models.py
It provides functions for saving a track, reading one, and displaying all 
tracks. It's the database layer and creates the SQLite database with two 
tables ("tracks" and "issues").

# test_checks.py
I wanted to ensure the engine couldn't crash silently, which is why I 
wrote automated tests with pytest. There are 18 of them, and they cover 
each rule with both a valid and invalid case, as well as tests for 
calculating the score.

# templates/
The HTML templates are:

"layout.html" : the basic layout with the navigation bar.

"index.html" : the home page with the form.

"about.html" : the page explaining the problem and the idea.

"report.html" : the results page displayed after an analysis

"report_pdf.html" : a separate, simpler template used only to generate the 
PDF report.

"history.html" : the list of all analyzed traces.

# static/styles.css
I wanted the app to look more professional, more like a B2B tool than a 
consumer product, so I chose a neutral color palette with dark blue 
accents to give it a professional touch, the custom CSS is based on 
Bootstrap.

# requirements.txt
The Python libraries used by the project (Flask, pytest, xhtml2pdf).


# Design choices

One function for each rule. I preferred to break it into small, 
independent pieces, even though I could have written all the validation 
logic in one long function. This way, I can test each rule individually 
and add a new one without changing the others. Plus, when I come back to 
it a few days later, it makes the code much easier to read.

Two database tables instead of one. Connected by a foreign key, I divided 
the data into tracks and issues. This would have made it impossible to ask 
questions about all the issues, such as "what's the most common error?", 
if I had kept everything in a single JSON field. With two tables, this 
type of query becomes trivial.

SQLite. Because it resides in a single file and doesn't require a server, 
I chose SQLite. For an MVP, it was the simplest and most functional 
choice.

Risk score. It loses 20 points for each red issue and 8 for each yellow 
issue, starting from 100: this is how the score works. It should carry 
more weight than a yellow issue, which only makes payment uncertain, 
because a red issue blocks royalty payments: this is my reasoning. This is 
a first approximation, not a definitive answer (see below).

A separate template for the PDF. It looks nice and uses Bootstrap, the 
browser reporting tool. However, it doesn't support Bootstrap well, the 
library I use to generate the PDF, xhtml2pdf. I created a second, simpler 
template, with only inline CSS, rather than counteracting the library. The 
PDF stays on a single page and has a clean look.

# Using AI

Throughout this project, I used an AI assistant (Claude) as a debbuging/programming 
tutor.

Because I believe honesty is more useful than pretending I built 
everything without any help, I want to be transparent about how I did it.

I believe taht in the near future, using AI will be part of the journey.

As suggested in the last lesson, I would also like to thank the course for 
allowing me to use AI to implement and speed up processes.

I used AI to:

Choose a project with a real market problem at its core.

It helped me do research on the music industry and its regulations.

It helped me understanding on things hadn't covered in depth during CS50, 
and get support in implementing parts of Flask, SQLite, and Pytest where 
needed.

I also learned more about VS Code installed locally on my Pc.

When I got stuck (a missing template file, a non-active virtual 
environment, issues with local enviroment), I used it to debbug unknown errors due 
to my limitations.

I used AI also to translate some sentences due to lenguage limitaions.

# My Final Thoughts

The final score is a indicative estimate. Count the issues by number, not by actual 
financial impact. if compared to a song with three minor issues, a song with a 
very serious error (such as splits that add up to 110%, thus blocking all 
royalties) can still get a higher score. Depending on the amount of money 
actually at risk, a real next step would be to assign a specific weight to 
each rule.

There is no real connection to industry registries. This tool would 
communicate with SIAE (Italy), ASCAP, or MLC through licensed partnerships 
in a full version. So, this MVP version focuses on product/project 
validation, because these integrations are not currently available as free APIs.

Name consistency checking is essential. Only different spaces and 
case are detected. To manage cases like "Riccardo Durante" and "R. 
Durante" as if they were the same person, a better full version of "PreFlight" 
would use approximate matching.

Thank you.


# More documentation

For a deeper look at the product thinking behind PreFlight:
- [Product Brief](docs/PROJECT_BRIEF.md) — problem, market, users, competition
- [Roadmap](docs/ROADMAP.md) — completed work and planned phases
- [Decision Log](docs/DECISION_LOG.md) — key decisions with context and reasoning