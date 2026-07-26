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

### What did I learn from the failed unique-word test?

I learned that automated tests can contain mistakes too. When a test fails, I
should verify both the implementation and the expected result instead of
automatically assuming that the application code is wrong. In this case, the
program correctly found three unique words, but the test incorrectly expected
four.

###