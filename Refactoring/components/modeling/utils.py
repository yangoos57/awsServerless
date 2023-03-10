from sklearn.metrics.pairwise import cosine_similarity
from typing import Union, Tuple
from model import SentenceBert
from collections import Counter
from konlpy.tag import Hannanum
from itertools import chain
import pandas as pd
import torch


class keywordExtractor:
    def __init__(self, model, tokenizer, noun_extractor: Hannanum = None) -> None:
        self.model = model
        self.tokenizer = tokenizer
        self.sbert = SentenceBert(model, tokenizer)
        self.sbert.eval()
        if not noun_extractor:
            self.noun_extractor = Hannanum()

    def extract_keywords(self, doc: pd.Series, min_count: int = 2, min_length: int = 2):
        doc_list = self._convert_series_to_keywords_list(doc)
        doc_list = self._map_english_to_hangeul(doc_list)
        candidate_keywords = self._extract_candidate_keywords(
            doc_list, self.noun_extractor, min_count
        )
        candidate_keywords = list(filter(lambda x: len(x) >= min_length, candidate_keywords))
        return candidate_keywords

    def _convert_series_to_keywords_list(self, series: pd.Series) -> str:
        book_title = series["title"]
        series = series.drop(["title", "isbn13"])

        raw_data = [book_title] + list(chain(*series.values))
        return list(chain(*map(lambda x: x.split(), raw_data)))

    def _map_english_to_hangeul(self, word_list: list[str]) -> list[str]:
        eng_han_df = pd.read_csv("../../data/preprocess/englist.csv")
        eng_han_dict = dict(eng_han_df.values)
        return list(map(lambda x: self._map_eng_to_han(x, eng_han_dict), word_list))

    def _map_eng_to_han(self, word: str, eng_han_dict: dict) -> str:
        han_word = eng_han_dict.get(word)
        return han_word if han_word else word

    def _extract_candidate_keywords(
        self, words: list[str], noun_extractor: Hannanum, min_count: int = 3
    ) -> list[str]:

        # extract han keywords
        han_words = noun_extractor.nouns(" ".join(words))
        han_candidate_words = filter(lambda x: x[1] >= min_count, Counter(han_words).items())

        # extract eng keywords
        def is_eng(words: str) -> bool:
            return True if words.encode().isalpha() else False

        eng_words = filter(is_eng, words)
        eng_candidate_words = filter(lambda x: x[1] >= min_count, Counter(eng_words).items())

        # merge keywords
        candidate_words = dict(chain(han_candidate_words, eng_candidate_words)).keys()

        return list(candidate_words)

    def extract_keyword_embedding(self, tokenized_keywords: torch.Tensor) -> torch.Tensor:

        # extract attention_mask, keywords_embedding
        attention_mask = tokenized_keywords["attention_mask"]
        keywords_embedding = self.model(**tokenized_keywords)["last_hidden_state"]

        # optimize attention_mask, keywords_embedding
        attention_mask, optimized_keywords_embedding = self._delete_cls_sep(
            attention_mask, keywords_embedding
        )

        # mean pooling
        keywords_embedding = self._pool_keyword_embedding(
            attention_mask, optimized_keywords_embedding
        )

        return keywords_embedding

    def tokenize_keywords(self, text: Union[list[str], str], max_length=128):
        token = self.tokenizer(
            text,
            truncation=True,
            padding=True,
            max_length=max_length,
            stride=20,
            return_overflowing_tokens=True,
            return_tensors="pt",
        )
        token.pop("overflow_to_sample_mapping")
        return token

    def _delete_cls_sep(
        self, attention_mask: torch.Tensor, keywords_embedding: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        attention_mask = attention_mask.detach().clone()
        keywords_embedding = keywords_embedding.detach().clone()

        # delete [cls], [sep] in attention_mask
        num_keywords = attention_mask.size(0)
        for i in range(num_keywords):
            sep_idx = (attention_mask[i] == 1).nonzero(as_tuple=True)[0][-1]
            attention_mask[i][0] = 0  # [CLS] => 0
            attention_mask[i][sep_idx] = 0  # [SEP] => 0

        # delete [cls], [sep] in keywords_embedding
        boolean_mask = attention_mask.unsqueeze(-1).expand(keywords_embedding.size()).float()
        keywords_embedding = keywords_embedding * boolean_mask

        return attention_mask, keywords_embedding

    def _pool_keyword_embedding(
        self, attention_mask: torch.Tensor, keywords_embedding: torch.Tensor
    ) -> torch.Tensor:

        num_of_tokens = attention_mask.unsqueeze(-1).expand(keywords_embedding.size()).float()
        total_num_of_tokens = num_of_tokens.sum(1)
        total_num_of_tokens = torch.clamp(total_num_of_tokens, min=1e-9)

        sum_embeddings = torch.sum(keywords_embedding, 1)

        # Mean Pooling
        mean_pooling = sum_embeddings / total_num_of_tokens
        return mean_pooling
