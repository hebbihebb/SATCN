from pipeline.filters.t5_grammar_filter import T5GrammarFilter

text = '''i dont even know why im writting this lol, like its 3am an my brain wont stop spinning 🤦‍♀️ everything feels like a movie but the kind that got low budget n no one showed up. he said he loved me but then he left like two minits later?? idk maybe its me or maybe ppl just like drama more than peace. anyways im sittin here eatin cold pizza an thinkin abt the way his eyes use to glow in the dark (prolly cuz of the phone screen but whatever).

my freind jess keeps texting me sayin “girl u deserve better” but she also dated that dude with the skull tat n 3 baby mamas so who even listens anymore 😂. i tried to write a poem but it turned into like a rant?? here it goes:

roses are red
my phone is broke
ur name on my screen
was a cosmic joke

idc if that dont rhyme im not a english teacher okay. i just wanna sleep but also i dont want tomorrow to come cuz then its monday an mondays r like emotional hangovers.'''

def main():
    print("Loading T5 model (this may take a while on first run)...")
    t5_filter = T5GrammarFilter()
    print("\nOriginal text:\n")
    print(text)
    print("\nCorrected text:\n")
    corrected = t5_filter.correct_text(text)
    print(corrected)

if __name__ == "__main__":
    main()
