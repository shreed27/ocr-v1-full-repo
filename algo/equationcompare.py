#!/usr/bin/env python
#coding:utf-8
"""
  Author:   --<Swagat>
  Purpose:
        Handels all the equation compairsion between
        standard answer and student answer.
  Created: Tuesday 28 October 2014
"""
# built-in packages
import traceback
import re
import math
from collections import Counter


class EquationCompare(object):
    """
    Purpose:
        To compare the equations between two sentences
    Description:
        In this class, initial arggument is student answer list.
        It's main executing function name is (compare).
        The function have following arguments.
            standard_answer_list
        It will return a dictionary as
            1. Key = "EqnResult"
                Value = Bool, (True if correct ans also if no equation)
            2. Key = "EqnCos",
                Value = The cosine_similarity value.
            3. Key = "EqnSimilar",
                Value = std_points_list contains eqution.
    """

    def __init__(self, stu_sentecelist):
        """
        Constructor
        The intial argument is answer_sentencelist,
        which will use to strore the equations in a list.
        """
        self.stu_sentece_text = stu_sentecelist
        # Student sentence attributes
        self.stu_equationlist = list()
        if self.stu_sentece_text:
            self.stu_equationlist = self.get_equation("Student")
        # Standard sentence attributes
        self.std_equationlist = list()
        self.std_sentencelist = list()
        # Optional attributes
        self.relaxtation_value = 0.1
        self.eqn_threshold = 0.9
        self.oporater = dict(_pos="+",
                             _neg="-",
                             _eql="=",
                             _grt=">",
                             _lsr="<")

    def get_equation(self, who):
        """
        Purpose:
            Responsible for extract equations from sentence.
        Arrguments:
            "who" = Identifier, whom equation has to extract(Teacher, Student).
        Description:
            The equation is in text is started with '$$' symbol
            to identify bet'n equation and word
            If Teacher,
                Text is in the list of dict, Key = 'KeyS'
            If Student,
               Text is in the dict, Key = 'StuS'.
            Split with space, check weather the value is started with "$$".
            Store the True values in the list.
        Return:
            Returns a list which will have equation
            Sample = ['\\frac{d}{dx}=\\sqrt{x}', '\\sumx^1+abc=d^2']
        """
        _text = ""
        equationlist = list()
        try:
            if who == "Teacher":
                _text += str(self.std_sentencelist['KeyS'])
            elif who == "Student":
                _text = self.stu_sentece_text
        except KeyError as exp:
            print 'Exception at eqn extraction in get_equation = ', exp
            traceback.print_exc()
        else:
            if _text:
                _textsplit = _text.split()
                equationlist = [_word.strip("$$")
                                for _word in _textsplit
                                if _word and _word.startswith("$$")]
        return equationlist

    @staticmethod
    def get_word(eqn):
        """
        Purpose: To get continuous word which is mixed
        with "*"
        Arrguments:
            The equation
        Description:
            Store in a temperary variable until non word raise
        Return:
            The list of word
        """
        temp = ""
        # pattern to get word or * in each character
        temp_word_pett = re.compile(r'^(\w+\*+|\*+\w+|\w+|\*+)')
        # pattern for next word or * in string
        next_word_pett = re.compile(r'(\w+|\*+)')
        word_list = list()
        while eqn:
            match = temp_word_pett.search(eqn)
            if not match:
                if temp:
                    word_list.append(temp)
                temp = ""
                next_match = next_word_pett.search(eqn)
                if not next_match:
                    break
                eqn = eqn[next_match.start():]
                continue
            temp += match.group(0)
            eqn = eqn[match.end(0) : ]
            if not eqn and temp:
                word_list.append(temp)            
        return word_list

    def get_cosine(self, c_std_eqn, c_stu_eqn):
        """
        Purpose:
            Compare two equations & return float value
        Arrguments:
            c_std_eqn = standard equation
            c_stu_eqn = student equation
        Description:
            Convert both to vector structure,
            calculate the no * in std word,
            calculate the no * in stu word,
            subtract both for only variable count,
            calculate % of * in std word
            get common word, Apply cosine similarity
            formula, Now add both value to get final result
        Return:
            cosine value(float) in between 0 ~ 1
        """
        std_vector = Counter(self.get_word(c_std_eqn))
        stu_vector = Counter(self.get_word(c_stu_eqn))
        _special_symbol = 0
        non_intersection_value = list()
        # Storing number of * & the value contains *
        for _val in std_vector.keys():
            if _val.__contains__("*"):
                _special_symbol += std_vector[_val]
                non_intersection_value.append(_val)
        if stu_vector.has_key("*"):
            _special_symbol -= stu_vector["*"]
        intersection = set(std_vector.keys()) & set(stu_vector.keys())
        numerator = sum([std_vector[x] * stu_vector[x]
                         for x in intersection])
        non_intersection_sum = 0
        # storing no of non_matched value
        for _val in stu_vector.keys():
            if _val not in intersection:
                non_intersection_sum += stu_vector[_val]
                non_intersection_value.append(_val)
        # If both non intersect value are not same
        # Empty the list
        if _special_symbol != non_intersection_sum:
            non_intersection_value = list()
        # Cosine similarity formula
        _sum1 = sum([std_vector[x]**2
                     for x in std_vector.keys()
                     if x not in non_intersection_value])
        _sum2 = sum([stu_vector[x]**2
                     for x in stu_vector.keys()
                     if x not in non_intersection_value])
        denominator = math.sqrt(_sum1) * math.sqrt(_sum2)
        if not denominator:
            return 0
        else:
            return (float(numerator) / denominator) \
                   if (float(numerator) / denominator) <= 1.0 \
                   else 1

    def calculate_oporater(self, o_std_eqn, o_stu_eqn):
        """
        Purpose:
            Check if same number of operator
        Arrguments:
            o_std_eqn = standard equation
            o_stu_eqn = student equation
        Description:
            Iterate operators, store the no in two list.
            Compare two lists
        Return:
            Boolean
            True : Same number of operator
            False : Not same
        """
        std_oporater_list = list()
        stu_oporater_list = list()
        for _symbol in self.oporater.values():
            std_oporater_list.append(o_std_eqn.count(_symbol))
            stu_oporater_list.append(o_stu_eqn.count(_symbol))
        if std_oporater_list == stu_oporater_list:
            return True
        else:
            return False

    def compare(self, std_sentence):
        """
        Purpose:
            It is the main function, to call all funtion in an
            order to compare one sentence's equations
            with all student equation.
        Arrguments:
            std_sentence is one sentence dict which have
            one text.
        Description:
            Empty standard equation list, store new.
            Check if std ans have equation,
            Return EqnResult=True for empty.
            Check number of operator in both equation.
            Call get_cosine function
            Check if lake percentage of equation is
            less than relaxtation value
        Return:
            A dictionary
            1. Key = "EqnResult"
                Value = Bool, (True if correct ans also if no equation)
            2. Key = "EqnSimilar",
                Value = dict("equation":cosine similarity).
        """
        correct_cos_value = 0
        final_dict = dict()
        eqn_similar = dict()
        self.std_sentencelist = std_sentence
        self.std_equationlist = self.get_equation("Teacher")
        if not self.std_equationlist:
            # Teacher's sentence doesn't have equation,
            # So Full value for continue word analisys
            final_dict = dict(EqnResult=True, EqnSimilar=eqn_similar)
            return final_dict
        for _std_eqn in self.std_equationlist:
            for _stu_eqn in self.stu_equationlist:
                oporater_check = self.calculate_oporater(_std_eqn, _stu_eqn)
                if oporater_check:
                    # Get cosine value in bet'n two equation[0~1]
                    cos_value = self.get_cosine(_std_eqn, _stu_eqn)
                    # save only maximum match value(should be greater than 0.9)
                    # can be changed as demand
                    if cos_value > self.eqn_threshold and \
                       not eqn_similar.has_key(_std_eqn):
                        correct_cos_value += float(cos_value)
                        eqn_similar[_std_eqn] = float(cos_value)
        # Check if total lale of cos values of all equations in
        # standard answer list is less than relaxtation_value
        lake_value = len(self.std_equationlist) - correct_cos_value \
            if len(self.std_equationlist) >= correct_cos_value \
            else self.relaxtation_value
        if self.relaxtation_value > lake_value:
            final_dict = dict(EqnResult=True, EqnSimilar=eqn_similar)
        else:
            final_dict = dict(EqnResult=False, EqnSimilar=eqn_similar)
        return final_dict
