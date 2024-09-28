import os
import numpy as np
import textstat


class TextAnalyzer:
    def __init__(self):
        pass
        
    def __str__(self):
        return "Transcript Video using Whisper"
        
    
    def gunning_fog(self, text: str) -> float:
        """
        The `gunning_fog` function calculates the Gunning Fog index for a given text.
        
        :param text: The `text` parameter in the `gunning_fog` function is expected to be a string
        containing the text for which you want to calculate the Gunning Fog index. This text can be a
        passage, an article, a document, or any other piece of written content for which you want to
        :type text: str
        :return: The `gunning_fog` readability score of the input text is being returned.
        """
        return textstat.gunning_fog(text)
    
    
    def readibility(self, text: str) -> tuple[float, float, float]:
        """
        This Python function calculates readability scores for a given text using the Flesch Reading
        Ease, Flesch-Kincaid Grade Level, and Dale-Chall Readability formulas.
        
        :param text: The code snippet you provided is a function named `readibility` that takes a string
        input `text` and calculates three readability scores using the `textstat` library: Flesch
        Reading Ease, Flesch-Kincaid Grade Level, and Dale-Chall Readability Score. The function
        :type text: str
        :return: The function `readibility` is returning a tuple containing three float values:
        `reading_ease`, `grade`, and `dale_chall`.
        """
        reading_ease = textstat.flesch_reading_ease(text)
        grade = textstat.flesch_kincaid_grade(text)    
        dale_chall = textstat.dale_chall_readability_score(text)
        
        return reading_ease, grade, dale_chall
    
    
ta = TextAnalyzer()
text = "W obniżeniu ulega oprocentowanie oferowanych obligacji przy jednoczesnym zachowaniu preferencji dla rynku detalicznego względem rynku hurtowego dedykowanego inwestorom instytucjonalnym."
gf = ta.gunning_fog(text)
print(f"GF: {gf}")
reading_ease, grade, dale_chall = ta.readibility(text)
print(f"Flesch reading ease: {reading_ease} | Flesch-Kincaid grade: {grade} | Dale-Chall Readibility Score: {dale_chall}")
        
        