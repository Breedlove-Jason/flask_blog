"""Public project notes; maintained in source independently of reader accounts."""
NOTES = [
    {
        "slug": "rebuilding-pacman",
        "title": "What rebuilding Pacman taught us about game state",
        "subtitle": "Small lifecycle bugs can change the entire feel of a game.",
        "category": "JavaScript",
        "body": """<p>A browser game makes state-management problems visible. An extra keyboard listener changes movement after a restart. A blocked ghost can freeze a game loop. The order of collision checks determines whether a power pellet protects the player in time.</p>
<h2>One game, one input handler</h2><p>The Pacman modernization keeps a single keyboard handler and clears the previous timer before starting another run. Restarting resets the board, score, characters, and power state together.</p>
<h2>Finite movement choices</h2><p>Instead of repeatedly guessing a direction until one works, a ghost chooses from the available directions. When none are open, it waits. That makes a blocked position a normal game state rather than an endless loop.</p>
<h2>Order matters</h2><p>Pellets are collected before collisions are resolved. A queued turn waits for an open junction, while pause preserves the remaining power duration. These small details make the controls more predictable.</p>
<h2>Keeping the original character</h2><p>The project retains its original maze and CSS characters. Native JavaScript modules replace the old bundler, and touch controls make the game usable beyond a desktop keyboard.</p><p><a href="https://pacman.jasonbreedlove.dev">Play Pacman</a> · <a href="https://github.com/Breedlove-Jason/pacman-js">Explore the code</a></p>"""
    },
    {
        "slug": "reuters-document-similarity",
        "title": "Finding related news with n-grams",
        "subtitle": "An explainable search experiment across Reuters-21578.",
        "category": "Python & data",
        "body": """<p>Reuters Similarity Lab compares news articles through shared sequences of words. It is an experiment in lexical overlap: the score describes shared text, not whether two articles mean the same thing.</p>
<h2>From words to sets</h2><p>A unigram is one word, a bigram is two consecutive words, and a trigram is three. Each article becomes a set of these sequences. Jaccard similarity divides the number of shared sequences by the number of distinct sequences across both articles.</p>
<h2>The full corpus</h2><p>The downloader verifies the complete 22-file Reuters-21578 collection. Its 21,578 records include 19,043 nonempty article bodies that can be indexed. Records without a body remain accounted for.</p>
<h2>Doing less work per query</h2><p>An inverted index records which articles contain each sequence. Search considers articles sharing query sequences instead of comparing every article from scratch. In the recorded benchmark, all 30 top-five rankings matched an exhaustive reference.</p>
<h2>Where this approach stops</h2><p>Word overlap does not understand synonyms or paraphrases. Larger n-grams preserve more phrase structure but become more sensitive to wording. The notebook makes those tradeoffs visible through queries, plots, and reproducible measurements.</p><p><a href="https://github.com/Breedlove-Jason/reuters-similarity-lab">Read the experiment and open the notebook</a></p>"""
    },
    {
        "slug": "building-field-notes",
        "title": "Turning a Flask exercise into Field Notes",
        "subtitle": "A blog needs publishing, persistence, and something worth reading.",
        "category": "Flask",
        "body": """<p>Field Notes began as a Flask learning project with accounts, posts, and comments. Preparing it for a public portfolio required checking the complete path from a form submission to a database row and back to a readable page.</p>
<h2>Identity is not display text</h2><p>A post belongs to a user through an integer foreign key. Storing the author's name in that field breaks the relationship. The corrected publishing flow stores the user ID and displays the related author's name.</p>
<h2>Publishing is a separate permission</h2><p>Registering an account permits participation in comments. Editorial access is configured separately. No account becomes an editor just because it was the second person to register.</p>
<h2>Writes need deliberate requests</h2><p>Deleting content now requires a POST request with CSRF protection. Comments render as plain text, while article HTML passes through an allowlist before display.</p>
<h2>Deployment is more than a successful build</h2><p>A deployed application can connect to a database and still fail because its tables do not exist. Database initialization and an editor account are part of launch, alongside the code and hosting configuration.</p><p><a href="https://github.com/Breedlove-Jason/flask_blog">Explore Field Notes on GitHub</a></p>"""
    },
]
