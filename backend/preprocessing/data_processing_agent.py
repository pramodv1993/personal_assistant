"""
1. iterate over the files in the data directory
2. invoke the data processing agent by passing a snippet of the content
"""

import os
from pathlib import Path

from agent_builder import construct_data_processing_graph


def get_snippet(file_path):
    return open(file_path, "r").read(768)


if __name__ == "__main__":
    graph = construct_data_processing_graph
    data_dir = Path("./preprocessing/data/")
    file_names = os.listdir(data_dir)
    for file_name in file_names:
        file_path = data_dir / file_name
        graph.invoke(
            {
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
        )
