import pandas as pd
import os
from load_files import load_diffs
from pattern_mining import get_code_snippets, normalize_block

def main():
    # Executing in wrong directory or missing data
    if not os.path.exists("../data"):
        print('You are either missing the data folder or executing from the wrong directory. \nMake sure to execute the code within the src folder.')
        return

    # Load diffs and make snippets
    data = load_diffs('all_diffs_new.jsonl')
    snippets = get_code_snippets(data)

    # Turn our data into more maleable format
    df_meta = pd.read_csv('../data/fixes_score_65.csv')
    df_snip = pd.DataFrame(snippets)

    # Normalize commit hash
    df_snip['hash_clean'] = df_snip['commit'].str[-40:]
    df_meta['hash_clean'] = df_meta['hash'].str[-40:]

    # Merge both
    merged = df_snip.merge(df_meta, on='hash_clean', how='inner')
    print('Merged rows:', len(merged))

    # This is essentially the same as merged because all score is above this threshold
    df_filtered = merged[merged["score"] >= 65].reset_index(drop=True)
    print("Rows of the filtered score:", len(df_filtered))

    df_snip.to_csv('../data/diff_snippets_readable.csv', index=False)
    merged.to_csv('../data/merged_full_dataset.csv', index=False)

    # Building normalized text from added + deleted code
    merged["text_norm"] = (
        merged["added_code"].fillna("").apply(normalize_block)
        + " "
        + merged["deleted_code"].fillna("").apply(normalize_block)
    )

    merged.to_csv('../data/normalized_merged_df.csv', index=False)
    print("Saved as normalized_merged_df.csv")

    df_filtered = merged[merged["score"] >= 65].reset_index(drop=True)
    df_filtered.to_csv("../data/normalized_merged_df_score65.csv", index=False)
    print("Rows of the filtered score:", len(df_filtered))


    

if __name__ == '__main__':
    main()