# coding: utf-8

from __future__ import unicode_literals
from  normalizer.Utils import *
import html2text
import string

compile_patterns = lambda patterns: [(re.compile(pattern), repl) for pattern, repl in patterns]


class Normalizer(object):
    def __init__(self, language='fa',
                 remove_extra_spaces=True,
                 rtl_style=True,
                 rtl_numbers_refinement=True,
                 remove_diacritics=True,
                 affix_spacing=True,
                 remove_repeated_chars=False,
                 punctuation_spacing=True,
                 hashtags_refinement=False,
                 entity_cleaning=False,
                 remove_punctuation=False,
                 remove_email=False,
                 remove_url=False,
                 remove_mobile_number=False,
                 remove_home_number=False,
                 remove_emoji=False,
                 remove_mention=False,
                 remove_html=False,
                 remove_numbers=False,
                 remove_english=False,
                 remove_newline=False):

        self.language = language
        self._punctuation_spacing = punctuation_spacing
        self._affix_spacing = affix_spacing
        self._remove_html = remove_html
        self._remove_punctuation = remove_punctuation
        self._hashtags_refinement = hashtags_refinement

        translation_src, translation_dst = ' كي“”', ' کی""'
        if self.language == 'ar':
            translation_src += "إأآاىؤئةگ"
            translation_dst += "اااايءءههك"
        elif self.language not in ['fa', 'ar']:
            translation_src, translation_dst = '', ''
        self.translations = maketrans(translation_src, translation_dst)

        if rtl_numbers_refinement:
            self.number_trans = maketrans(EN_NUMBERS, FA_NUMBERS)

        self.character_refinement_patterns = []

        if remove_extra_spaces:
            self.character_refinement_patterns.extend(EXTRA_SPACE)

        if rtl_style:
            self.character_refinement_patterns.extend(RTL_STYLE)

        if remove_diacritics:
            self.character_refinement_patterns.append(
                DIACRITIC_CHARS, )  # remove FATHATAN, DAMMATAN, KASRATAN, FATHA, DAMMA, KASRA, SHADDA, SUKUN

        if remove_repeated_chars:
            self.character_refinement_patterns.append(REPEATED_CHARS, )

        self.character_refinement_patterns = compile_patterns(self.character_refinement_patterns)

        if punctuation_spacing:
            self.punctuation_spacing_patterns = compile_patterns(PUNCTUATION_SPACE)

        if self.language == 'fa' and affix_spacing:
            self.affix_spacing_patterns = compile_patterns(AFFIX_SPACE)

        self.replace_patterns = []
        if remove_numbers:
            self.replace_patterns.append(NUMBER_REGEX)
        if remove_english:
            self.replace_patterns.append(ENGLISH_REGEX)
        if remove_email or entity_cleaning:
            self.replace_patterns.append(EMAIL_REGEX)
        if remove_url or entity_cleaning:
            self.replace_patterns.append(URL_REGEX)
        if remove_mobile_number or entity_cleaning:
            self.replace_patterns.append(MOBILE_PHONE_REGEX)
        if remove_emoji or entity_cleaning:
            self.replace_patterns.append(EMOJI_REGEX)
        if remove_home_number or entity_cleaning:
            self.replace_patterns.append(HOME_PHONE_REGEX)
        if remove_mention or entity_cleaning:
            self.replace_patterns.append(MENTION_REGEX)
        if remove_newline:
            self.replace_patterns.append(NEWLINE_REGEX)


    def replace_entities(self, text):
        if self._remove_html:
            text = html2text.html2text(text)
        for pattern in self.replace_patterns:
            text = pattern.sub('', text)
        if self._hashtags_refinement:
            text = self.hashtag_refinment(text)
        if self._remove_punctuation:
            text = text.translate(str.maketrans('', '', string.punctuation + '،؛«»'))
        return text

    def normalize(self, text):
        text = self.replace_entities(text)
        text = self.character_refinement(text)
        if self.language == 'fa' and self._affix_spacing:
            text = self.affix_spacing(text)
        if self._punctuation_spacing:
            text = self.punctuation_spacing(text)
        return text

    def character_refinement(self, text):
        text = text.translate(self.translations)
        if self.number_trans:
            text = text.translate(self.number_trans)
        for pattern, repl in self.character_refinement_patterns:
            text = pattern.sub(repl, text)
        return text

    def punctuation_spacing(self, text):
        for pattern, repl in self.punctuation_spacing_patterns:
            text = pattern.sub(repl, text)
        return text

    def affix_spacing(self, text):
        for pattern, repl in self.affix_spacing_patterns:
            text = pattern.sub(repl, text)
        return text

    def hashtag_refinment(self, text):
        hashtags = re.findall(HASHTAG_REGEX, text)
        for tag in hashtags:
            repl_tag = tag.replace('#', '').replace('_', ' ')
            text = text.replace(tag, repl_tag)
        return text

    def get_language(self):
        return self.language
