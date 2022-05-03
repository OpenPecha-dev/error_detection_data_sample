import configparser
from pathlib import Path
from typing import List, Union

from lm import (
  LanguageModel,
  LSTMLanguageModel,
  GPT2LanguageModel,
  RoBERTaLanguageModel,
  LanguageModelType,
  ScoreType
)


class OptionsRanker:
  """Ranks word options in a given sentence"""
  
  def __init__(self, config_path=Path(__file__).parent/"config.ini"):
    self.config = configparser.ConfigParser()
    self.config.read(config_path)
    self.lm = self._load_lm()
    
  def _load_lm(self) -> LanguageModel:
    lm_type = LanguageModelType(self.config["ranker"]["lm_type"])
    lm_path = self.config[lm_type]["path"]
    if lm_type == LanguageModelType.LSTMLanguageModel:
      return LSTMLanguageModel(path=lm_path)
    elif lm_type == LanguageModelType.GPT2LanguageModel:
      return GPT2LanguageModel(path=lm_path)
    elif lm_type == LanguageModelType.RoBERTa:
      return RoBERTaLanguageModel(path=lm_path)
    
  def _check_input(self, left_context, right_context):
    if self.lm.pre_tokenize:
      if not isinstance(left_context, list) or not isinstance(right_context, list):
        raise ValueError("`context` should be list of word")
    else:
      if not isinstance(left_context, str) or not isinstance(right_context, str):
        raise ValueError("`context` should be string")
        
  def _create_sentence(self, option, left_context, right_context):
    if self.lm.pre_tokenize:
      return " ".join(left_context + [option] + right_context)
    return left_context + option + right_context
    
    
  def rank(
    self,
    options: List[str],
    left_context: Union[List[str], str],
    right_context: Union[List[str], str]
  ) -> List[str]:
    """return `options` in ranking order"""
    self._check_input(left_context, right_context)
    ranks = []
    for option in options:
      sentence = self._create_sentence(option, left_context, right_context)
      # print(sentence)
      score = self.lm.score_sentence(sentence)
      ranks.append((option, score))
    return sorted(
      ranks,
      key=lambda x: x[1],
      reverse=True if self.lm.score_type == ScoreType.PROB else False
    )
  
  
if __name__ == "__main__":
  ranker = OptionsRanker()
  ranks = ranker.rank(
    options=["འི", "གི", "དི"],
    left_context="བདེ་ཆེན་པདྨ་འཁྱིལ་བ",
    right_context="ཕོ་བྲང་ན"
  )
  # ranks = ranker.rank(
  #   options=["འི", "གི", "དི"],
  #   left_context=["བདེ་ཆེན་", "པདྨ་",  "འཁྱིལ་བ"],
  #   right_context=["ཕོ་བྲང་", "ན"]
  # )
  print(ranks)
 