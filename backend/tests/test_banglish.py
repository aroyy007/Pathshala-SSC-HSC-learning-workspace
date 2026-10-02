from eduapp.banglish import looks_banglish


def test_detects_banglish_question():
    assert looks_banglish("Anupomer bhaggo debota kake bola hoyeche?")
    assert looks_banglish("Kollyanir boyos koto chilo?")


def test_does_not_misclassify_bengali_or_ordinary_english():
    assert not looks_banglish("অনুপমের ভাগ্য দেবতা কে?")
    assert not looks_banglish("What is the central theme of this poem?")
