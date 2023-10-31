import pickle
import os
import re
from g2p_en import G2p

from text import symbols, punctuation

current_file_path = os.path.dirname(__file__)
CMU_DICT_PATH = os.path.join(current_file_path, "cmudict.rep")
CACHE_PATH = os.path.join(current_file_path, "cmudict_cache.pickle")
_g2p = G2p()

arpa = {
    "AH0",
    "S",
    "AH1",
    "EY2",
    "AE2",
    "EH0",
    "OW2",
    "UH0",
    "NG",
    "B",
    "G",
    "AY0",
    "M",
    "AA0",
    "F",
    "AO0",
    "ER2",
    "UH1",
    "IY1",
    "AH2",
    "DH",
    "IY0",
    "EY1",
    "IH0",
    "K",
    "N",
    "W",
    "IY2",
    "T",
    "AA1",
    "ER1",
    "EH2",
    "OY0",
    "UH2",
    "UW1",
    "Z",
    "AW2",
    "AW1",
    "V",
    "UW2",
    "AA2",
    "ER",
    "AW0",
    "UW0",
    "R",
    "OW1",
    "EH1",
    "ZH",
    "AE0",
    "IH2",
    "IH",
    "Y",
    "JH",
    "P",
    "AY1",
    "EY0",
    "OY2",
    "TH",
    "HH",
    "D",
    "ER0",
    "CH",
    "AO1",
    "AE1",
    "AO2",
    "OY1",
    "AY2",
    "IH1",
    "OW0",
    "L",
    "SH",
}


def post_replace_ph(ph):
    rep_map_post = {
        "：": ",",
        "；": ",",
        "，": ",",
        "。": ".",
        "！": "!",
        "？": "?",
        "\n": ".",
        "·": ",",
        "、": ",",
        "...": "…",
    }
    if ph in rep_map_post.keys():
        ph = rep_map_post[ph]
    if ph in symbols:
        return ph
    if ph not in symbols:
        ph = "UNK"
    return ph


def read_dict():
    g2p_dict = {}
    start_line = 49
    with open(CMU_DICT_PATH) as f:
        line = f.readline()
        line_index = 1
        while line:
            if line_index >= start_line:
                line = line.strip()
                word_split = line.split("  ")
                word = word_split[0]

                syllable_split = word_split[1].split(" - ")
                g2p_dict[word] = []
                for syllable in syllable_split:
                    phone_split = syllable.split(" ")
                    g2p_dict[word].append(phone_split)

            line_index = line_index + 1
            line = f.readline()

    return g2p_dict


def cache_dict(g2p_dict, file_path):
    with open(file_path, "wb") as pickle_file:
        pickle.dump(g2p_dict, pickle_file)


def get_dict():
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, "rb") as pickle_file:
            g2p_dict = pickle.load(pickle_file)
    else:
        g2p_dict = read_dict()
        cache_dict(g2p_dict, CACHE_PATH)

    return g2p_dict


eng_dict = get_dict()


def refine_ph(phn):
    tone = 0
    if re.search(r"\d$", phn):
        tone = int(phn[-1]) + 1
    return phn, tone


def refine_syllables(syllables):
    tones = []
    phonemes = []
    for phn_list in syllables:
        for i in range(len(phn_list)):
            phn = phn_list[i]
            phn, tone = refine_ph(phn)
            phonemes.append(phn)
            tones.append(tone)
    return phonemes, tones


import re
import inflect

_inflect = inflect.engine()
_comma_number_re = re.compile(r"([0-9][0-9\,]+[0-9])")
_decimal_number_re = re.compile(r"([0-9]+\.[0-9]+)")
_pounds_re = re.compile(r"£([0-9\,]*[0-9]+)")
_dollars_re = re.compile(r"\$([0-9\.\,]*[0-9]+)")
_ordinal_re = re.compile(r"[0-9]+(st|nd|rd|th)")
_number_re = re.compile(r"[0-9]+")

# List of (regular expression, replacement) pairs for abbreviations:
_abbreviations = [
    (re.compile("\\b%s\\." % x[0], re.IGNORECASE), x[1])
    for x in [
        ("mrs", "misess"),
        ("mr", "mister"),
        ("dr", "doctor"),
        ("st", "saint"),
        ("co", "company"),
        ("jr", "junior"),
        ("maj", "major"),
        ("gen", "general"),
        ("drs", "doctors"),
        ("rev", "reverend"),
        ("lt", "lieutenant"),
        ("hon", "honorable"),
        ("sgt", "sergeant"),
        ("capt", "captain"),
        ("esq", "esquire"),
        ("ltd", "limited"),
        ("col", "colonel"),
        ("ft", "fort"),
    ]
]


# List of (ipa, lazy ipa) pairs:
_lazy_ipa = [
    (re.compile("%s" % x[0]), x[1])
    for x in [
        ("r", "ɹ"),
        ("æ", "e"),
        ("ɑ", "a"),
        ("ɔ", "o"),
        ("ð", "z"),
        ("θ", "s"),
        ("ɛ", "e"),
        ("ɪ", "i"),
        ("ʊ", "u"),
        ("ʒ", "ʥ"),
        ("ʤ", "ʥ"),
        ("ˈ", "↓"),
    ]
]

# List of (ipa, lazy ipa2) pairs:
_lazy_ipa2 = [
    (re.compile("%s" % x[0]), x[1])
    for x in [
        ("r", "ɹ"),
        ("ð", "z"),
        ("θ", "s"),
        ("ʒ", "ʑ"),
        ("ʤ", "dʑ"),
        ("ˈ", "↓"),
    ]
]

# List of (ipa, ipa2) pairs
_ipa_to_ipa2 = [
    (re.compile("%s" % x[0]), x[1]) for x in [("r", "ɹ"), ("ʤ", "dʒ"), ("ʧ", "tʃ")]
]


_arpa_to_ipa = {
    # Vowels - Monophthongs
    "AO": "ɔ",
    "AO0": "ɔ",
    "AO1": "ɔ",
    "AO2": "ɔ",
    "AA": "ɑ",
    "AA0": "ɑ",
    "AA1": "ɑ",
    "AA2": "ɑ",
    "IY": "i",
    "IY0": "i",
    "IY1": "i",
    "IY2": "i",
    "UW": "u",
    "UW0": "u",
    "UW1": "u",
    "UW2": "u",
    "EH": "ɛ",
    "EH0": "ɛ",
    "EH1": "ɛ",
    "EH2": "ɛ",
    "IH": "ɪ",
    "IH0": "ɪ",
    "IH1": "ɪ",
    "IH2": "ɪ",
    "UH": "ʊ",
    "UH0": "ʊ",
    "UH1": "ʊ",
    "UH2": "ʊ",
    "AH": "ə",
    "AH0": "ə",
    "AH1": "ə",
    "AH2": "ə",
    "AE": "æ",
    "AE0": "æ",
    "AE1": "æ",
    "AE2": "æ",
    "AX": "ə",
    "AX0": "ə",
    "AX1": "ə",
    "AX2": "ə",
    # Vowels - Diphthongs
    "EY": "eɪ",
    "EY0": "eɪ",
    "EY1": "eɪ",
    "EY2": "eɪ",
    "AY": "aɪ",
    "AY0": "aɪ",
    "AY1": "aɪ",
    "AY2": "aɪ",
    "OW": "oʊ",
    "OW0": "oʊ",
    "OW1": "oʊ",
    "OW2": "oʊ",
    "AW": "aʊ",
    "AW0": "aʊ",
    "AW1": "aʊ",
    "AW2": "aʊ",
    "OY": "ɔɪ",
    "OY0": "ɔɪ",
    "OY1": "ɔɪ",
    "OY2": "ɔɪ",
    # Consonants - Stops
    "P": "p",
    "B": "b",
    "T": "t",
    "D": "d",
    "K": "k",
    "G": "g",
    # Consonants - Affricates
    "CH": "ʧ",
    "JH": "ʤ",
    # Consonants - Fricatives
    "F": "f",
    "V": "v",
    "TH": "θ",
    "DH": "ð",
    "S": "s",
    "Z": "z",
    "SH": "ʃ",
    "ZH": "ʒ",
    "HH": "h",
    # Consonants - Nasals
    "M": "m",
    "N": "n",
    "NG": "ŋ",
    # Consonants - Liquids
    "L": "l",
    "R": "r",
    # Vowels - R-colored vowels
    "ER": "ər",
    "ER0": "ər",
    "ER1": "ər",
    "ER2": "ər",
    "AXR": "ər",
    "AXR0": "ər",
    "AXR1": "ər",
    "AXR2": "ər",
    # Consonants - Semivowels
    "W": "w",
    "Y": "j",
    # Unknown
    "UNK": ",",
}


def _expand_dollars(m):
    match = m.group(1)
    parts = match.split(".")
    if len(parts) > 2:
        return match + " dollars"  # Unexpected format
    dollars = int(parts[0]) if parts[0] else 0
    cents = int(parts[1]) if len(parts) > 1 and parts[1] else 0
    if dollars and cents:
        dollar_unit = "dollar" if dollars == 1 else "dollars"
        cent_unit = "cent" if cents == 1 else "cents"
        return "%s %s, %s %s" % (dollars, dollar_unit, cents, cent_unit)
    elif dollars:
        dollar_unit = "dollar" if dollars == 1 else "dollars"
        return "%s %s" % (dollars, dollar_unit)
    elif cents:
        cent_unit = "cent" if cents == 1 else "cents"
        return "%s %s" % (cents, cent_unit)
    else:
        return "zero dollars"


def _remove_commas(m):
    return m.group(1).replace(",", "")


def _expand_ordinal(m):
    return _inflect.number_to_words(m.group(0))


def _expand_number(m):
    num = int(m.group(0))
    if num > 1000 and num < 3000:
        if num == 2000:
            return "two thousand"
        elif num > 2000 and num < 2010:
            return "two thousand " + _inflect.number_to_words(num % 100)
        elif num % 100 == 0:
            return _inflect.number_to_words(num // 100) + " hundred"
        else:
            return _inflect.number_to_words(
                num, andword="", zero="oh", group=2
            ).replace(", ", " ")
    else:
        return _inflect.number_to_words(num, andword="")


def _expand_decimal_point(m):
    return m.group(1).replace(".", " point ")


def normalize_numbers(text):
    text = re.sub(_comma_number_re, _remove_commas, text)
    text = re.sub(_pounds_re, r"\1 pounds", text)
    text = re.sub(_dollars_re, _expand_dollars, text)
    text = re.sub(_decimal_number_re, _expand_decimal_point, text)
    text = re.sub(_ordinal_re, _expand_ordinal, text)
    text = re.sub(_number_re, _expand_number, text)
    text = text.replace("&", "and")
    return text


rep_map = {
    "：": ",",
    "；": ",",
    "，": ",",
    ":": ",",
    "。": ".",
    "！": "!",
    "？": "?",
    "\n": ".",
    "．": ".",
    "...": " …",
    "···": " …",
    "・・・": " …",
    "·": ",",
    "・": ",",
    "、": ",",
    "$": ".",
    "“": "'",
    "”": "'",
    "‘": "'",
    "’": "'",
    '"': "'",
    "（": "'",
    "）": "'",
    "(": "'",
    ")": "'",
    "《": "'",
    "》": "'",
    "【": "'",
    "】": "'",
    "[": "'",
    "]": "'",
    "—": "-",
    "−": "-",
    "～": "-",
    "~": "-",
    "「": "'",
    "」": " '",
}


def replace_punctuation(text):
    pattern = re.compile("|".join(re.escape(p) for p in rep_map.keys()))

    replaced_text = pattern.sub(lambda x: rep_map[x.group()], text)
    return replaced_text


def text_normalize(text):
    text = normalize_numbers(text)
    text = replace_punctuation(text)
    return text


def g2p(text):
    phones = []
    tones = []
    word2ph = []
    text = text_normalize(text)
    words = re.split(r"([,;.\-\?\!\s+])", text)
    words = [word for word in words if word.strip() != ""]
    # temp = [word for word in words if word not in punctuation]
    # phn_list = ipa.convert(" ".join(temp)).split(" ")
    for word in words:
        temp_phones = []
        temp_tone = []
        if word.upper() in eng_dict:
            phns, tns = refine_syllables(eng_dict[word.upper()])
            temp_phones += phns
            temp_tone += tns
        else:
            try:
                phone_list = list(filter(lambda p: p != " ", _g2p(word)))
            except Exception as e:
                print(word)
                raise e
            for ph in phone_list:
                if ph in arpa:
                    ph, tn = refine_ph(ph)
                    temp_phones.append(ph)
                    temp_tone.append(tn)
                else:
                    temp_phones.append(ph)
                    temp_tone.append(0)
        if len(temp_phones) == 0:
            temp_phones = [post_replace_ph(word)]
        if len(temp_tone) == 0:
            temp_tone = [0] * len(temp_phones)
        # arpa_to_ipa
        for i in range(len(temp_phones)):
            if temp_phones[i] not in punctuation:
                temp_phones[i] = _arpa_to_ipa[temp_phones[i]]
                temp_phones[i] = re.sub(
                    r"l([^aeiouæɑɔəɛɪʊ ]*(?: |$))",
                    lambda x: "ɫ" + x.group(1),
                    temp_phones[i],
                )
                for regex, replacement in _ipa_to_ipa2:
                    temp_phones[i] = re.sub(regex, replacement, temp_phones[i])
            temp_tone[i] = [temp_tone[i]] * len(temp_phones[i])

        temp_phones = [i for j in temp_phones for i in j]
        phns = [post_replace_ph(ph) for ph in temp_phones]
        assert all([ph in symbols for ph in phns]), (words, phns)
        phones += phns
        tones += [j for i in temp_tone for j in i]
        word2ph.append(len(phns))
        # if word in punctuation:
        #     phones.append(post_replace_ph(word))
        #     word2ph.append(1)
        # else:
        #     phns = phn_list.pop(0)  # ipa.convert(word.lower())
        #     phns = re.sub(
        #         r"l([^aeiouæɑɔəɛɪʊ ]*(?: |$))", lambda x: "ɫ" + x.group(1), phns
        #     )
        #     for regex, replacement in _ipa_to_ipa2:
        #         phns = re.sub(regex, replacement, phns)
        #     assert all([ph in symbols for ph in list(phns)]), (words, phns)
        #     phones += list(phns)
        #     word2ph.append(len(phns))

    phones = ["_"] + phones + ["_"]
    tones = [0] + tones + [0]
    word2ph = [1] + word2ph + [1]
    assert len(phones) == len(tones)

    return phones, tones, word2ph


def get_bert_feature(text, word2ph):
    from text import english_bert_mock

    return english_bert_mock.get_bert_feature(text, word2ph)


if __name__ == "__main__":
    # print(get_dict())
    # print(eng_word_to_phoneme("hello"))
    print(g2p("In this paper, we propose 1 DSPGAN, a GAN-based universal vocoder."))
    # all_phones = set()
    # for k, syllables in eng_dict.items():
    #     for group in syllables:
    #         for ph in group:
    #             all_phones.add(ph)
    # print(all_phones)
