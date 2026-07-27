# Development Log

## Project Setup

### What is stylometry?

Stylometry is the study of measurable patterns in someone's wrting, such as, sentence length, word choice, punctuation, and vocabulary.

### What do I expect this application to measure?

Ecpectations for this application are to analyze writing patterns and help students/teachers understand the use of AI in writing submissions.

### Why can't writing patterns prove that text was AI-generated?

Technology today is not capable of 100% AI detection, this is merely a writing pattern analyzer.

### What part of the project structure is currently least familiar to me?

The tests folder is currently the least familiar to me. I understand that it will check whether the program works correctly, but I do not yet understand how a test file runs the code from the src folder. 

### What is "text.split()" and what does it do? 

text.split() separates text into pieces wherever it finds whitespace, then counts to pieces.

### Why does converting "Python", "PYTHON", and "python" to lowercase help us compare vocabulary?

Converting words to lowercase ensures that differently capitalized versions
of the same word are counted as one vocabulary item. This makes vocabulary
comparisons more consistent.

NOTE: There is an interesting tradeoff: capitalization itself can reveal writing habits. We removed it for vocabulary comparison, but we can measure unusual capitalization separately later. This is an important lesson in stylometry: preprocessing simplifies the text, but it can also remove potentially useful information.

### What was learned from the failed unique-word test?

Automated tests can contain mistakes too. When a test fails, you should verify both the implementation and the expected result instead of
automatically assuming that the application code is wrong. In this case, the
program correctly found three unique words, but the test incorrectly expected
four.

### What is one limitation of vocabulary richness?

Vocabulary richness is affected by document length. Longer documents usually
repeat more words, so comparing texts of very different lengths could produce
misleading results.

### What limitation is discovered in the sentence tokenizer?

The sentence tokenizer treated "Dr." as a complete sentence because it splits
text at every period. The regular expression recognizes punctuation patterns,
but it does not understand whether a period belongs to an abbreviation,
decimal number, or actual sentence ending.

### Why exclude internal punctuation from average word length?

A contraction or hyphenated expression is preserved as one word token, but
average word length is intended to count letters rather than punctuation.
Apostrophes and hyphens may still reveal writing habits, so the analyzer will
measure them separately instead of allowing them to distort word length.

### How to verify the punctuation tests were discovered?

The first run reported 17 tests instead of the expected 21. I recognized that
the four new tests had not been discovered, inspected my files, corrected the
issue, and reran the suite successfully with all 21 tests passing.

### Which profile entries are raw counts, and which are calculated or normalized measurements?

The raw counts are `word_count`, `unique_word_count`, and `sentence_count`.
They report how many items were observed directly.

The calculated or normalized measurements are `vocabulary_richness`,
`average_word_length`, `average_sentence_length`, and all punctuation rates
measured per 100 words. These values use ratios or averages to make writing
samples easier to compare, especially when the samples have different lengths.
Unique-word count and sentence count are also raw counts because they answer “how many?”rather than expressing an average, proportion, or rate.

### Why should we test invalid and missing files when the application is designed to analyze valid writing samples?

We test invalid and missing giles to ensure the application responds predictablywhen a user selects an unsupported format, misspells a filename, or moves a file. These tests do not analyze writing habits; they verify input validation and error handling. A clear error helps the user correct the problem and prevents the analyzer from processing or missing unreadable data.

### What did the first comparison reveal, and which result surprised me?

The first comparison produced nearly identical vocabulary-richness scores, so
that measurement did not meaningfully distinguish these two samples.

Both samples contained eight detected sentences. Words in the formal sample
averaged 5.89 letters, compared with 4.70 letters in the conversational sample.

The conversational sample had a slightly longer average sentence length of
14.63 words, compared with 14.0 words in the formal sample. This contradicted
our original prediction that conversational sentences would be shorter.

The takeaway is that we can form hypotheses, but we must allow measurements to
challenge them. We should not adjust our interpretation merely to match what we
expected. These two deliberately styled samples are also too limited to support
universal conclusions about formal and conversational writing.

### Why did we stop displaying jointly absent features as 100% similar?

Both samples having zero occurrences is a shared absence, but presenting it as
a full similarity bar could exaggerate the evidence of matching writing styles.
The revised chart marks these features as not scored, making the visualization
more transparent.

### What did I learn about quotation marks?

Quotation marks define the boundaries of strings. A single missing quotation
mark can cause Python or the shell to interpret later instructions as part of
an unfinished string. Unexpected continuation prompts such as `...` or
`dquote>` are signals to cancel the instruction and inspect matching quotation
marks before trying again.