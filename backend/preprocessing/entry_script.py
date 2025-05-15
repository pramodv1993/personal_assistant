import argparse
import os
from pathlib import Path

from agent_builder import construct_data_processing_graph


def get_snippet(file_path):
    return open(file_path, "r").read(768)


if __name__ == "__main__":
    """
    1. iterate over the files in the data directory
    2. invoke the data processing agent by passing a snippet of the content
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--model_type",
        help="describe if self hosted models or cloud models is to be used for processing",
        choices=["cloud", "self_hosted"],
        default="cloud",
    )
    args = parser.parse_args()
    graph = construct_data_processing_graph()
    data_dir = Path("data/")
    file_names = os.listdir(data_dir)
    for file_name in file_names:
        file_path = data_dir / file_name
        for chunk in graph.stream(
            input={
                "messages": [
                    {
                        "role": "user",
                        "content": f"""
                                    filepath: {file_path}
                                    snippet: {get_snippet(file_path)}
                                    """,
                    }
                ]
            }
        ):
            continue
            # print(chunk)
