
import re


FA_NUMBERS = '۰۱۲۳۴۵۶۷۸۹'
EN_NUMBERS = '0123456789%'
maketrans = lambda A, B: dict((ord(a), b) for a, b in zip(A, B))


DIACRITIC_CHARS = ('[\u064B\u064C\u064D\u064E\u064F\u0650\u0651\u0652]', '')
REPEATED_CHARS = (r'(.)\1+', r'\1')
EXTRA_SPACE = [
                (r' +', ' '),  # remove extra spaces
                (r'\n\n+', '\n\n'),  # remove extra newlines
                (r'[ـ\r]', ''),  # remove keshide, carriage returns
            ]
RTL_STYLE = [
                ('"([^\n"]+)"', r'«\1»'),  # replace quotation with gyoome
                ('([\d+])\.([\d+])', r'\1٫\2'),  # replace dot with momayez
                (r' ?\.\.\.', ' …'),  # replace 3 dots
            ]
punc_after, punc_before = r'\.:!،؛؟»\]\)\}', r'«\[\(\{'
PUNCTUATION_SPACE = [
                    ('" ([^\n"]+) "', r'"\1"'),  # remove space before and after quotation
                    (' ([' + punc_after + '])', r'\1'),  # remove space before
                    ('([' + punc_before + ']) ', r'\1'),  # remove space after
                    ('([' + punc_after[:3] + '])([^ \d' + punc_after + '])', r'\1 \2'),  # put space after . and :
                    ('([' + punc_after[3:] + '])([^ ' + punc_after + '])', r'\1 \2'),  # put space after
                    ('([^ ' + punc_before + '])([' + punc_before + '])', r'\1 \2'),  # put space before
                    ]
AFFIX_SPACE = [
                (r'([^ ]ه) ی ', r'\1‌ی '),  # fix ی space
                (r'(^| )(ن?می) ', r'\1\2‌'),  # put zwnj after می, نمی
                (r'(?<=[^\n\d ' + punc_after + punc_before + ']{2}) (تر(ین?)?|گری?|های?)(?=[ \n' + punc_after + punc_before + ']|$)',r'‌\1'),  # put zwnj before تر, تری, ترین, گر, گری, ها, های
                (r'([^ ]ه) (ا(م|یم|ش|ند|ی|ید|ت))(?=[ \n' + punc_after + ']|$)', r'\1‌\2'),
                # join ام, ایم, اش, اند, ای, اید, ات
             ]

PUNCTUATION_CHARS = re.compile('''!"#\$%&\'\(\)\*\+\,\-./:;<=>\?@\[\\]\^_`\{\|\}~،؛«»''')

# source: https://gist.github.com/dperini/729294
# @jfilter: I think it was changed
URL_REGEX = re.compile(
    r"(?:^|(?<![\w\/\.]))"
    # protocol identifier
    # r"(?:(?:https?|ftp)://)"  <-- alt?
    r"(?:(?:https?:\/\/|ftp:\/\/|www\d{0,3}\.))"
    # user:pass authentication
    r"(?:\S+(?::\S*)?@)?" r"(?:"
    # IP address exclusion
    # private & local networks
    r"(?!(?:10|127)(?:\.\d{1,3}){3})"
    r"(?!(?:169\.254|192\.168)(?:\.\d{1,3}){2})"
    r"(?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})"
    # IP address dotted notation octets
    # excludes loopback network 0.0.0.0
    # excludes reserved space >= 224.0.0.0
    # excludes network & broadcast addresses
    # (first & last IP address of each class)
    r"(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])"
    r"(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}"
    r"(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))"
    r"|"
    # host name
    r"(?:(?:[a-z\\u00a1-\\uffff0-9]-?)*[a-z\\u00a1-\\uffff0-9]+)"
    # domain name
    r"(?:\.(?:[a-z\\u00a1-\\uffff0-9]-?)*[a-z\\u00a1-\\uffff0-9]+)*"
    # TLD identifier
    r"(?:\.(?:[a-z\\u00a1-\\uffff]{2,}))" r"|" r"(?:(localhost))" r")"
    # port number
    r"(?::\d{2,5})?"
    # resource path
    r"(?:\/[^\)\]\}\s]*)?",
    # r"(?:$|(?![\w?!+&\/\)]))",
    # @jfilter: I removed the line above from the regex because I don't understand what it is used for, maybe it was useful?
    # But I made sure that it does not include ), ] and } in the URL.
    flags=re.UNICODE | re.IGNORECASE,
)

EMAIL_REGEX = re.compile(
    r"(?:^|(?<=[^\w@.)]))([\w+-](\.(?!\.))?)*?[\w+-](@|[(<{\[]at[)>}\]])(?:(?:[a-z\\u00a1-\\uffff0-9]-?)*[a-z\\u00a1-\\uffff0-9]+)(?:\.(?:[a-z\\u00a1-\\uffff0-9]-?)*[a-z\\u00a1-\\uffff0-9]+)*(?:\.(?:[a-z\\u00a1-\\uffff]{2,}))",
    flags=re.IGNORECASE | re.UNICODE,
)
ENGLISH_REGEX = re.compile(r'[A-Za-z]')
NEWLINE_REGEX = re.compile(R'\s{2,}')
NUMBER_REGEX = re.compile(r'[۰۱۲۳۴۵۶۷۸۹0-9]')
HASHTAG_REGEX = re.compile(r"(#\w+)")
MENTION_REGEX = re.compile(r"(^|[^@\w])@(\w{1,15})")
HOME_PHONE_REGEX = re.compile(r"(\d{8})|(0\d{2}[-]?\d{8})")
MOBILE_PHONE_REGEX = re.compile(r"((098|\+98)?(0)?9\d{9})")
EMOJI_REGEX = re.compile(pattern="["
                                     u"\U0001F600-\U0001F64F"  # emoticons
                                     u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                     u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                     u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                     u"\U00002500-\U00002BEF"  
                                     u"\U00002702-\U000027B0" 
                                     u"\U000024C2-\U0001F251" 
                                     u"\U0001f926-\U0001f937" 
                                     u"\U00010000-\U0010ffff" 
                                     u"\u2640-\u2642" 
                                     u"\u2600-\u2B55" 
                                     u"\u200d" u"\u23cf" u"\u23e9" u"\u231a" u"\ufe0f" u"\u3030"
                                    "]+", flags=re.UNICODE)
