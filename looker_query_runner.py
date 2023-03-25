import pandas as pd


class LookerQueryRunner:
    def __init__(self, sdk) -> None:
        self.sdk = sdk

    def run_query(self, write_query):
        query_result = self.sdk.run_inline_query("json", write_query)

        print(query_result)
        query_result_df = pd.read_json(query_result)

        # error if the query result is empty
        if query_result_df.empty:
            raise Exception("Query result is empty")

        return query_result_df
