import json
from dataclasses import asdict

from openai import OpenAI

from renamef.config import CONFIG
from renamef.prompts import system_instruction
from renamef.renamer import rename_files_function, rename_files
from renamef.file_reader import Result, list_files_function, read_file_function, list_files, read_file

# Example:
# contents = {
#     "image_content": {
#         "<tool_id1>": [2, {"type": "image_url"}, {"type": "image_url"}],
#         "<tool_id2>": [1, {"type": "image_url"}]
#     },
#     "tool_content": {
#         "<tool_id1>": Result,
#         "<tool_id2>": Result
#     }
# }


class Assistant:
    def __init__(self, thinking: bool = False):
        self.model = CONFIG["llm"]["model"]
        self.reasoning_effort = "none" if thinking is False else "medium"
        self.history: list = [{"role": "system", "content": system_instruction}]
        self.openrouter = OpenAI(base_url="http://127.0.0.1:11434/v1", api_key="ollama")
        self.tools = [
            {"type": "function", "function": list_files_function},
            {"type": "function", "function": read_file_function},
            {"type": "function", "function": rename_files_function}
        ]

    def chat(self, user_message: str) -> str | None:
        messages = self.history + [{"role": "user", "content": user_message}]
        response = self.openrouter.chat.completions.create(
            model=self.model,
            messages=messages,
            reasoning_effort=self.reasoning_effort,  # type: ignore
            tools=self.tools,  # type: ignore
        )
        # Add user message and LLM reply to history:
        # self.history.append({"role": "user", "content": user_message})
        if not response.choices[0].finish_reason == "tool_calls":
            self.history.append({"role": "assistant", "content": response.choices[0].message.content})

        while response.choices[0].finish_reason == "tool_calls":
            msg_4_tool = response.choices[0].message  # "message" holds the "role", "content", and "tool_calls" keys
            tool_result = Assistant.dispatcher(msg_4_tool)
            messages.append(msg_4_tool)
            messages.extend(tool_result)
            self.history = messages
            response = self.openrouter.chat.completions.create(
                model=self.model,
                messages=messages,
                reasoning_effort=self.reasoning_effort,  # type: ignore
                tools=self.tools,  # type: ignore
            )

        return response.choices[0].message.content

    def reset_history(self) -> None:
        self.history: list = [{"role": "system", "content": system_instruction}]

    @staticmethod
    def dispatcher(llm_msg) -> list[dict]:
        contents = {  # Store tool results in a dict. Example structure below
            "image_content": {},
            "tool_content": {}
        }
        # contents = {
        #     "image_content": {
        #         "<tool_id1>": [{"type": "image_url"}, {"type": "image_url"}],
        #         "<tool_id2>": [{"type": "image_url"}, {"type": "image_url"}]
        #     },
        #     "tool_content": {
        #         "<tool_id1>": str,
        #         "<tool_id2>": str
        #     }
        # }
        tool_registry = {
            "list_files": list_files,
            "read_file": read_file,
            "rename_files": rename_files}

        tool_calls = llm_msg.tool_calls  # "tool_calls" holds the "id", "type", and "function" keys
        for tool in tool_calls:
            for function in tool_registry:
                if tool.function.name not in tool_registry:
                    contents["tool_content"][tool.id] = f"ERROR: No such tool as '{tool.function.name}'"
                    break
                elif tool.function.name == function:
                    try:
                        arguments = json.loads(tool.function.arguments)  # "arguments" has dict of function arguments
                    except json.JSONDecodeError:
                        contents["tool_content"][tool.id] = "ERROR: Invalid JSON structure..."
                        break
                    try:
                        tool_result: Result = tool_registry[function](**arguments)
                    except TypeError:
                        contents["tool_content"][tool.id] = ("ERROR: Incorrect or misspelled argument(s) "
                                                             "or missing keyword...")
                        break
                    except Exception:
                        contents["tool_content"][tool.id] = "ERROR: Something went wrong..."
                        break

                    # Multiple images can be stored as a result of one tool call
                    if isinstance(tool_result, Result) and tool_result.text.startswith("image/"):
                        for b64 in tool_result.image:
                            image_url = f"data:{tool_result.text};base64,{b64}"
                            if tool.id not in contents["image_content"]:
                                img_nr = 1
                                contents["image_content"][tool.id] = [img_nr, {"type": "image_url",
                                                                      "image_url": {"url": image_url}}]
                            else:
                                contents["image_content"][tool.id].append({"type": "image_url",
                                                                           "image_url": {"url": image_url}})
                                contents["image_content"][tool.id][0] += 1  # Add 1 to img_nr in the list

                    else:
                        result_dict = asdict(tool_result)                   # turn Result object into a dict
                        result_json = json.dumps(result_dict, default=str)  # turn the dict into JSON format
                        if tool.id not in contents["tool_content"]:
                            contents["tool_content"][tool.id] = result_json
                    break

        # ----------------------- iterate over contents dict to produce a tool response ----------------------- #
        tool_messages = []
        if contents["tool_content"]:
            for tool_id in contents["tool_content"]:
                tool_messages.append({"role": "tool",
                                      "tool_call_id": tool_id,
                                      "content": contents["tool_content"][tool_id]
                                      })
        if contents["image_content"]:
            for tool_id in contents["image_content"]:
                img_nr = contents["image_content"][tool_id].pop(0)
                tool_messages.append({"role": "tool",
                                      "tool_call_id": tool_id,
                                      "content":
                                          f"{img_nr} images attached below in the same order as the image tool calls"
                                      })
            tool_messages.append({"role": "user",
                                  "content": [img_content
                                              for tool_id in contents["image_content"]
                                              for img_content in contents["image_content"][tool_id]
                                              ]})
        return tool_messages
