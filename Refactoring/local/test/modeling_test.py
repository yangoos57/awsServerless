import sys

sys.path.append("../")

from components.modeling import keywordExtractor
from utils import read_pkl
import pandas as pd

if __name__ == "__main__":
    ###
    # load extractor
    extractor = keywordExtractor(dir="../data/preprocess/eng_han.csv")

    ###
    # load test files
    test_df = pd.read_parquet("data/modeling_test.parquet")
    test_series = test_df.iloc[0]
    test_result = read_pkl("data/modeling_test_result")

    ###
    # test extract_keyword_list method
    def test_extract_keyword_list():
        assert test_result["extract_keyword_list"] == extractor.extract_keyword_list(test_series)

        assert test_result[
            "_convert_series_to_keyword_list"
        ] == extractor._convert_series_to_keyword_list(test_series)

        assert test_result["_map_english_to_hangeul"] == extractor._map_english_to_hangeul(
            test_result["_convert_series_to_keyword_list"]
        )

        assert test_result["_extract_candidate_keyword"] == extractor._extract_candidate_keyword(
            test_result["_map_english_to_hangeul"]
        )

    ###
    # test create_keyword_embedding method
    def create_keyword_embedding():
        assert test_result["create_keyword_embedding"] == extractor.create_keyword_embedding(
            test_series
        )

        assert test_result["tokenize_keyword"] == extractor.tokenize_keyword(
            test_result["extract_keyword_list"]
        )

        assert test_result["_create_keyword_embedding"] == extractor._create_keyword_embedding(
            test_result["tokenize_keyword"]
        )

    ###
    # test create_doc_embeddings method
    def create_doc_embeddings():
        assert test_result["create_doc_embeddings"] == extractor.create_doc_embeddings(test_series)

        assert test_result["_convert_series_to_str"] == extractor._convert_series_to_str(
            test_series
        )

        assert test_result["tokenize_doc"] == extractor.tokenize_keyword(
            test_result["_convert_series_to_str"]
        )

        assert test_result["_create_doc_embeddings"] == extractor._create_doc_embeddings(
            test_result["tokenize_keyword"]
        )

    ###
    # test extract_keyword method
    def extract_keyword():
        assert test_result["extract_keyword"] == extractor.extract_keyword(test_df)

        assert test_result["_calc_cosine_similarity"] == extractor._calc_cosine_similarity(
            test_result["create_doc_embeddings"], test_result["create_keyword_embedding"]
        )

        assert test_result["_filter_top_n_keyword"] == extractor._filter_top_n_keyword(
            test_result["extract_keyword_list"], test_result["_calc_cosine_similarity"].flatten()
        )
