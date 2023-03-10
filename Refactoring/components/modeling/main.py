from transformers import ElectraModel, ElectraTokenizerFast
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import numpy as np
from utils import *


if __name__ == "__main__":
    # load sentence beart
    model = ElectraModel.from_pretrained("monologg/koelectra-base-v3-discriminator")
    tokenizer = ElectraTokenizerFast.from_pretrained("monologg/koelectra-base-v3-discriminator")

    # load data
    raw_data = pd.read_parquet("../../data/book_scraping.parquet")

    key = keywordExtractor(model, tokenizer)

    print(key.extract_keywords(raw_data.iloc[0]))
