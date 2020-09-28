class Words:
    __unit = {0: "zero",1: "one", 2: "two", 3: "three", 4: "four",
              5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine",
               10: "ten", 11: "eleven", 12: "twelve", 13: "thirteen",
               14: "fourteen", 15: "fifteen", 16: "sixteen",
               17: "seventeen", 18: "eighteen", 19: "nineteen"}

    __ten = {2: "twenty", 3: "thirty", 4: "forty", 5: "fifty",
                 6: "sixty", 7: "seventy", 8: "eighty", 9: "ninety"}

    def __tens(self, value):
        """function to define the tens"""
        value1 = int(value / 10)
        if (value >= 1) and (value < 20):
            return self.__unit[value]
        elif (value % 10) == 0:
            return self.__ten[value1]
        else:
            return self.__ten[value1] + "-" + self.__unit[value % 10]

    def __hundred(self, value):
        value1 = int(value/100)
        temp_value = value % 100
        if temp_value == 0:
            return self.__unit[value1] + " hundred"
        elif value1 == 0:
            return self.__tens(value % 100)
        else:
            return self.__unit[value1] + " hundred and " + self.__tens(value % 100)

    def __hundreds(self, value):
        value1 = int(value/100)
        temp_value = value % 100
        if temp_value == 0:
            return self.__unit[value1] + " hundred"
        elif value1 == 0:
            return " and " + self.__tens(value % 100)
        else:
            return self.__unit[value1] + " hundred and " + self.__tens(value % 100)

    def __thousands(self, value):
        value1 = int(value/1000)
        value2 = value % 1000
        if value2 == 0:
            return self.__hundred(value1) + " thousand"
        return self.__hundred(value1) +" thousand, "+ self.__hundreds(value2)

    def __millions(self, value):
        value1 = int(value/1000000)
        value2 = int(value%1000000)
        if value2 == 0:
            return self.__hundred(value1)+" million"
        return self.__hundred(value1) +" million, "+ self.__thousands(value2)

    def __billions(self, value):
        value1 = int(value/1000000000)
        value2 = int(value/1000000000)
        if value2 == 0:
            return self.__hundred(value1) + " billion"
        return self.__hundred(value1) + " billion, "+ self.__millions(value2)

    def __trillions(self, value):
        value1 = int(value/1000000000000)
        value2 = int(value%1000000000000)
        if value2 == 0:
            return self._hundred(value1) + " trillion"
        return self.__hundred(value1) + " trillion, "+ self.__billions(value2)

    def __whole_numbers(self, value):
        if (value >= 0) and (value < 10):
            return self.__unit[value]
        elif (value >= 10) and (value < 100):
            return self.__tens(value)
        elif (value >= 100) and (value < 1000):
            return self.__hundreds(value)
        elif (value >= 1000) and (value < 1000000):
            return self.__thousands(value)
        elif (value >= 1000000) and (value < 1000000000):
            return self.__millions(value)
        elif (value >= 1000000000) and (value < 1000000000000):
            return self.__billions(value)
        elif (value >=1000000000000) and (value < 1000000000000000):
            return self.__trillions(value)
        else:
            return "value out of range"

    def __decimals(self, value):
        """This function is not efficient. It needs to be reconstructed using the string builder class"""
        value1 = str(value)
        pos = value1.index('.')
        decimal = value1[pos+1:]
        output = " point "
        for variable in decimal:
            output += self.__unit[int(variable)] + " "
        return output

    def word(self, value):
        if (value % 1) == 0:
            return self.__whole_numbers(int(value))
        elif (value % 1) != 0:
            return self.__whole_numbers(int(value)) + self.__decimals(value)
        else:
            return "enter in a number"


class Exponent:
    number = Words()


# oga = Words()
#
# while True:
#     values = float(input("Enter in a number: "))
#     print(oga.word(values))


class Numbers:
    __numwords = {"and": (1, 0), "zero": (1, 0), "one": (1, 1), "two": (1, 2),
                  "three": (1, 3), "four": (1, 4), "five": (1, 5), "six": (1, 6),
                  "seven": (1, 7), "eight": (1, 8), "nine": (1, 9), "ten": (1, 10),
                  "eleven": (1, 11), "twelve": (1, 12), "thirteen": (1, 13),
                  "fourteen": (1, 14), "fifteen": (1, 15), "sixteen": (1, 16),
                  "seventeen": (1, 17), "eighteen": (1, 18), "nineteen": (1, 19),
                  "twenty": (1, 20), "thirty": (1, 30), "forty": (1, 40),
                  "fifty": (1, 50), "sixty": (1, 60), "seventy": (1, 70),
                  "eighty": (1, 80), "hundred": (100, 0), "thousand": (1000, 0),
                  "million": (1000000, 0), "billion": (1000000000, 0),
                  "trillion": (1000000000000, 0)}
    __numbers = {"zero": 0, "one": 1, "two": 2, "three": 3, "four": 4,
                 "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9}

    def number(self, textnum:str):
        """This function would take care of calling both decimal and whole numbers"""
        var1 = textnum.find('point')
        decimal = 0
        if var1 >= 0:
            textnum = textnum.replace('point', '')
            var2 = textnum[var1:]
            textnum = textnum.replace(var2, '')
            decimal += self.__decimal_number(var2)

        decimal += self.__whole_number(textnum)
        return decimal

    def __decimal_number(self, textnum:str):
        """This function would take care of the decimal part of the function"""
        textnum = self.__form(textnum)
        decimal = 0
        for idx, word in enumerate(textnum.split()):
            if word not in self.__numbers:
                raise Exception("Illegal word: " + word)
            decimal += self.__numbers[word] * (10 ** -(idx+1))

        return decimal

    def __whole_number(self, textnum:str) -> int:
        """This function would take care of the whole number part of the function"""
        textnum = self.__form(textnum)
        current = result = 0
        for word in textnum.split():
            if word not in self.__numwords:
                raise Exception("Illegal word: " + word)
            scale, increment = self.__numwords[word]
            current = current * scale + increment
            if scale > 100:
                result += current
                current = 0

        return result + current

    def __form(self, textnum:str) -> str:
        textnum = textnum.replace(',', ' ')
        textnum = textnum.replace('-', ' ')
        textnum = textnum.replace('_', ' ')
        textnum = textnum.lower()
        return textnum



# def is_number(x):
#    """look into this when you want to find words in string"""
#     if type(x) == str:
#         x = x.replace(',', '')
#     try:
#         float(x)
#     except:
#         return False
#     return True
#
# def text2int(textnum, numwords = {}):
#     units = ['zero', 'one', 'two', 'three', 'four', 'five',
#              'six', 'seven', 'eight', 'nine', 'ten', 'eleven',
#              'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen',
#              'seventeen', 'eighteen', 'nineteen']
#
#     tens = ['', '', 'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy',
#             'eighty', 'ninety']
#
#     scales = ['hundred', 'thousand', 'million', 'billion', 'trillion']
#     ordinal_words = {'first': 1, 'second': 2, 'third': 3, 'fifth': 5,
#                      'eighth': 8, 'ninth': 9, 'twelfth': 12}
#     ordinal_endings = [('ieth', 'y'), ('th', '')]
#
#     if not numwords:
#         numwords['and'] = (1, 0)
#         for idx, word in enumerate(units):
#             numwords[word] = (1, idx)
#         for idx, word in enumerate(tens):
#             numwords[word] = (1, idx * 10)
#         for idx, word in enumerate(scales):
#             numwords[word] = (10 ** (idx * 3 or 2), 0)
#
#         textnum = textnum.replace('-', ' ')
#
#         current = result = 0
#         curstring = ''
#         onnumber = False
#         lastunit = False
#         lastscale = False
#
#         def is_numword(x):
#             if is_number(x):
#                 return True
#             if word in numwords:
#                 return True
#             return False
#
#         def from_numword(x):
#             if is_number(x):
#                 scale = 0
#                 increment = int(x.replace(',', ''))
#             return numwords[x]
#
#         for word in textnum.split():
#             if word in ordinal_words:
#                 scale, increment = (1, ordinal_words[word])
#                 current = current * scale + increment
#                 if scale > 100:
#                     result += current
#                     current = 0
#                 onnumber = True
#                 lastunit = False
#                 lastscale = False
#             else:
#                 for ending, replacement in ordinal_endings:
#                     if word.endswith(ending):
#                         word = "%s%s" % (word[:-len(ending)], replacement)
#
#                 if(not is_numword(word)) or (word == 'and' and not lastscale):
#                     if onnumber:
#                         curstring += repr(result + current) + " "
#                     curstring += word + " "
#                     result = current = 0
#                     onnumber = False
#                     lastunit = False
#                     lastscale = False
#                 else:
#                     scale, increment = from_numword(word)
#                     onnumber = True
#
#                     if lastunit and (word not in scales):
#                         curstring += repr(result + current)
#                         result = current = 0
#
#                     if scale > 1:
#                         current = max(1, current)
#
#                     current = current * scale + increment
#                     if scale > 100:
#                         result += current
#                         current = 0
#
#                     lastscale = False
#                     lastunit = False
#                     if word in scales:
#                         lastscale = True
#                     elif word in units:
#                         lastunit = True
#     if onnumber:
#         curstring += repr(result + current)
#
#     return curstring
