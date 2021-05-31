import re
import sys

class Sentence:
    def __init__(self, answer, number, question, selection1, selection2, selection3):
        self.answer = answer
        self.number = number
        self.question = question
        self.selection1 = selection1
        self.selection2 = selection2
        self.selection3 = selection3

def normalizeUnfinishedQuestion(string):
    # remove last 。
    if string.endswith('。'):
        string = string[:-1]

    regexp = re.compile(r"(.+)(\(1\).+\(2\).+\(3\).+\s+)([^a-zA-Z]+.+)")
    match = regexp.search(string)
    if match is None or match.group(1).strip().endswith("？") or match.group(1).strip().endswith("?"):
        return string
    else:
        reformatted = match.group(1).strip() + " ____ " + match.group(3).strip() + match.group(2).strip()
        # print(reformatted)
        return reformatted


def normalize(string):
    string = string.replace("\t", ' ')
    string = string.replace('（', '(')
    string = string.replace('）', ')')

    if string.strip().endswith(')'):
        leftIndex = string.rfind('(')
        string = string[:leftIndex]

    return string.strip()

def validateInvalidLine(string):
    if not string.startswith('('):
        raise Exception('Invalid line detected:'+ string)

def findCategories(string):
    if string.endswith('〕'):
        regexp = re.compile("(.+)〔(.+)〕$")
        match = regexp.search(string)
        return (match.group(1).strip(), match.group(2).strip())
    elif string.endswith('］'):
        regexp = re.compile("(.+)［(.+)］$")
        match = regexp.search(string)
        return (match.group(1).strip(), match.group(2).strip())
    elif string.endswith('」'):
        regexp = re.compile("(.+)「(.+)」$")
        match = regexp.search(string)
        return (match.group(1).strip(), match.group(2).strip())
    elif string.endswith('﹞'):
        regexp = re.compile("(.+)﹝(.+)﹞$")
        match = regexp.search(string)
        return (match.group(1).strip(), match.group(2).strip())
    elif string.endswith('】'):
        regexp = re.compile("(.+)【(.+)】$")
        match = regexp.search(string)
        return (match.group(1).strip(), match.group(2).strip())
    else:
        return (string.strip(), '')

answerMapping = {
    '1': 'A',
    '2': 'B',
    '3': 'C',
    '4': 'D',
    '5': 'E'
}

def removeContainer(string):
    if string[0] == '(' and string[2] == ')':
        return string[3:]
    return string

def tokenize(string):
    regexp = re.compile(r"(.+)(\(1\).+)(\(2\).+)(\(3\).+)")
    match = regexp.search(string)
    anserAndQuestion = match.group(1).strip()
    selection1 = removeContainer(match.group(2).strip())
    selection2 = removeContainer(match.group(3).strip())
    selection3 = removeContainer(match.group(4).strip())

    regexp = re.compile(r"\((.+)\)\s*(\w+)\.\s*(.+)")
    match = regexp.search(anserAndQuestion)

    answer = ''
    for ans in match.group(1).strip():
        answer += answerMapping[ans]

    number = match.group(2).strip()
    question = match.group(3).strip()

    return Sentence(answer, number, question, selection1, selection2, selection3)

lineByCategories = {}
with open(sys.argv[1], 'r', encoding='utf-8') as fp:
    for line in fp:
        normalized_line = normalize(line)

        validateInvalidLine(normalized_line)

        [body, category] = findCategories(normalized_line)
        body = normalizeUnfinishedQuestion(body)
        lineByCategories.setdefault(category, []).append(tokenize(body))

with open(sys.argv[1][:-4] + '.tsv', 'w', encoding='utf-8') as fp:
    for category, sentences in lineByCategories.items():
        for sentence in sentences:
            if len(sentence.selection3) > len(sentence.selection1) * 3:
                print("Notice: [TOO LONG] Question:" + sentence.number)
            fp.write("{0}\t{1}\t{2} *** {3} *** {4}\n".format(sentence.answer, sentence.question, sentence.selection1, sentence.selection2, sentence.selection3))