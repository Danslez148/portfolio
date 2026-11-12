# MIPS Assembly Programs

Low-level programs written in MIPS assembly for the QtSpim simulator. They work with files and binary data through system calls.

- `question1.asm`, `question2.asm`: read a WAV file and parse its header (channels, sample rate, byte rate, bits per sample)
- `question3.asm`: process a WAV file's sample data and write the result to a new file
- `question4.asm`: generate a tone and write it out as a WAV file

**Context:** CSC2002S Computer Architecture, UCT (2024). Individual.

## Run
Load a file in [QtSpim](https://spimsimulator.sourceforge.net/) and run it. Each program prompts for its inputs (file names, and for `question4.asm` the tone frequency, sample rate and length).

`question1.asm` and `question2.asm` also run in [MARS](https://github.com/dpetersanderson/MARS). `question3.asm` and `question4.asm` need QtSpim: they open their output file with the Linux flags `577` (`O_WRONLY | O_CREAT | O_TRUNC`), which QtSpim passes to the operating system but MARS doesn't support, so under MARS no output file is written.
