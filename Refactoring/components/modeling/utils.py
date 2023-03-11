from sklearn.metrics.pairwise import cosine_similarity
from typing import Union, Tuple
from .model import SentenceBert
from collections import Counter
from konlpy.tag import Hannanum
from itertools import chain, islice
import pandas as pd
import numpy as np
import torch


class keywordExtractor:
    def __init__(self, model, tokenizer, noun_extractor: Hannanum = None, dir: str = None) -> None:
        self.model = model
        self.tokenizer = tokenizer
        self.sbert = SentenceBert(model, tokenizer)
        self.sbert.eval()

        if not noun_extractor:
            self.noun_extractor = Hannanum()
        else:
            self.noun_extractor = noun_extractor

        if not dir:
            self.dir = "../../data/preprocess/englist.csv"
        else:
            self.dir = dir

    def extract_keyword_list(self, doc: pd.Series, min_count: int = 3, min_length: int = 2) -> list:
        keyword_list = self._convert_series_to_keyword_list(doc)
        keyword_list = self._map_english_to_hangeul(keyword_list)
        candidate_keyword = self._extract_candidate_keyword(keyword_list, min_count)
        return list(filter(lambda x: len(x) >= min_length, candidate_keyword))

    def _convert_series_to_keyword_list(self, series: pd.Series) -> str:
        book_title = series["title"]
        series = series.drop(["title", "isbn13"])

        raw_data = [book_title] + list(chain(*series.values))
        return list(chain(*map(lambda x: x.split(), raw_data)))

    def _map_english_to_hangeul(self, word_list: list[str]) -> list[str]:
        eng_han_df = pd.read_csv(self.dir)
        eng_han_dict = dict(eng_han_df.values)

        def map_eng_to_han(word: str, eng_han_dict: dict) -> str:
            han_word = eng_han_dict.get(word)
            return han_word if han_word else word

        return list(map(lambda x: map_eng_to_han(x, eng_han_dict), word_list))

    def _extract_candidate_keyword(self, words: list[str], min_count: int = 3) -> list[str]:

        # extract han keyword
        han_words = self.noun_extractor.nouns(" ".join(words))
        han_candidate_words = filter(lambda x: x[1] >= min_count, Counter(han_words).items())

        # extract eng keyword
        def is_eng(words: str) -> bool:
            return True if words.encode().isalpha() else False

        eng_words = filter(is_eng, words)
        lower_eng_words = map(lambda x: x.lower(), eng_words)
        eng_candidate_words = filter(lambda x: x[1] >= min_count, Counter(lower_eng_words).items())

        # merge keyword
        candidate_words = dict(chain(han_candidate_words, eng_candidate_words)).keys()
        return list(candidate_words)

    def create_keyword_embedding(self, doc: pd.Series) -> torch.Tensor:
        keyword_list = self.extract_keyword_list(doc)
        tokenized_keyword = self.tokenize_keyword(keyword_list)
        return self._create_keyword_embedding(tokenized_keyword)

    def tokenize_keyword(self, text: Union[list[str], str], max_length=128) -> dict:
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

    def _create_keyword_embedding(self, tokenized_keyword: dict) -> torch.Tensor:

        # extract attention_mask, keyword_embedding
        attention_mask = tokenized_keyword["attention_mask"]
        keyword_embedding = self.model(**tokenized_keyword)["last_hidden_state"]

        # optimize attention_mask, keyword_embedding
        attention_mask, optimized_keyword_embedding = self._delete_cls_sep(
            attention_mask, keyword_embedding
        )

        # mean pooling
        keyword_embedding = self._pool_keyword_embedding(
            attention_mask, optimized_keyword_embedding
        )

        return keyword_embedding

    def _delete_cls_sep(
        self, attention_mask: torch.Tensor, keyword_embedding: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        attention_mask = attention_mask.detach().clone()
        keyword_embedding = keyword_embedding.detach().clone()

        # delete [cls], [sep] in attention_mask
        num_keyword = attention_mask.size(0)
        for i in range(num_keyword):
            sep_idx = (attention_mask[i] == 1).nonzero(as_tuple=True)[0][-1]
            attention_mask[i][0] = 0  # [CLS] => 0
            attention_mask[i][sep_idx] = 0  # [SEP] => 0

        # delete [cls], [sep] in keyword_embedding
        boolean_mask = attention_mask.unsqueeze(-1).expand(keyword_embedding.size()).float()
        keyword_embedding = keyword_embedding * boolean_mask
        return attention_mask, keyword_embedding

    def _pool_keyword_embedding(
        self, attention_mask: torch.Tensor, keyword_embedding: torch.Tensor
    ) -> torch.Tensor:

        num_of_tokens = attention_mask.unsqueeze(-1).expand(keyword_embedding.size()).float()
        total_num_of_tokens = num_of_tokens.sum(1)
        total_num_of_tokens = torch.clamp(total_num_of_tokens, min=1e-9)

        sum_embeddings = torch.sum(keyword_embedding, 1)

        # Mean Pooling
        mean_pooling = sum_embeddings / total_num_of_tokens
        return mean_pooling

    def create_doc_embeddings(self, doc: pd.Series) -> torch.Tensor:
        stringfied_doc = self._convert_series_to_str(doc)
        tokenized_doc = self.tokenize_keyword(stringfied_doc)
        return self._create_doc_embeddings(tokenized_doc)

    def _convert_series_to_str(self, series: pd.Series) -> str:
        book_title = series["title"]
        series = series.drop(["title", "isbn13"])
        return book_title + " " + " ".join(list(chain(*series.values)))

    def _create_doc_embeddings(self, tokenized_doc):
        return self.sbert(**tokenized_doc)["sentence_embedding"]

    def extract_keyword(self, docs: pd.DataFrame) -> dict:
        keyword_embedding = map(lambda x: self.create_keyword_embedding(x[1]), docs.iterrows())
        doc_embedding = map(lambda x: self.create_doc_embeddings(x[1]), docs.iterrows())
        keyword_list = map(lambda x: self.extract_keyword_list(x[1]), docs.iterrows())

        co_sim_score = map(
            lambda x: self._calc_cosine_similarity(*x).flatten(),
            zip(doc_embedding, keyword_embedding),
        )
        top_n_keyword = list(
            map(lambda x: self._filter_top_n_keyword(*x), zip(keyword_list, co_sim_score))
        )
        return dict(zip(docs["isbn13"].values, top_n_keyword))

    def _calc_cosine_similarity(
        self, doc_embedding: torch.Tensor, keyword_embedding: torch.Tensor
    ) -> np.array:

        doc_embedding = doc_embedding.detach()
        keyword_embedding = keyword_embedding.detach()

        doc_score = list(
            map(lambda x: cosine_similarity(x.unsqueeze(0), keyword_embedding), doc_embedding)
        )

        max_pooling = np.max(doc_score, axis=0)  # Max
        return max_pooling

    def _filter_top_n_keyword(
        self, keyword_list: list, co_sim_score: np.array, rank: int = 20
    ) -> list:
        keyword = dict(zip(keyword_list, co_sim_score))
        sorted_keyword = sorted(keyword.items(), key=lambda k: k[1], reverse=True)
        return list(dict(islice(sorted_keyword, rank)).keys())
