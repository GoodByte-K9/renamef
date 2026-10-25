from dataclasses import asdict
import json

from openai import OpenAI

from file_reader import Result, list_files_function, read_file_function, list_files, read_file
from prompts import system_instruction
from renamer import rename_files_function, rename_files
from config import CONFIG


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

        # TODO: LLM failed to follow up with another tool call. Why?
        while response.choices[0].finish_reason == "tool_calls":
            msg_4_tool = response.choices[0].message  # "message" holds the "role", "content", and "tool_calls" keys
            tool_result = Assistant.dispatcher(msg_4_tool)
            self.history.append(msg_4_tool)
            self.history.extend(tool_result)
            messages = self.history
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
    def dispatcher(llm_msg) -> list[dict] | str:
        def tool_response(content, tool_id):
            return [{"role": "tool", "content": content, "tool_call_id": tool_id}]

        tool_call = llm_msg.tool_calls[0]  # "tool_calls" holds the "id", "type", and "function" keys
        tool_registry = {
            "list_files": list_files,
            "read_file": read_file,
            "rename_files": rename_files}
        for tool in tool_registry:
            if tool_call.function.name == tool:
                arguments = json.loads(tool_call.function.arguments)  # "arguments" holds a dict of function arguments
                tool_result = tool_registry[tool](**arguments)
                data_urls = []

                if isinstance(tool_result, Result) and tool_result.text.startswith("image/"):
                    img_nr = 0
                    for b64 in tool_result.image:
                        image_url = f"data:{tool_result.text};base64,{b64}"
                        data_urls.append({"type": "image_url", "image_url": image_url})
                        img_nr += 1

                    response_to_llm = [
                        {"role": "tool",
                         "tool_call_id": tool_call.id,
                         "content": f"Loaded {img_nr} images — attached below."},
                        {"role": "user",
                         "content": data_urls}]
                    return response_to_llm
                else:
                    result_dict = asdict(tool_result)                   # turn Result object into a dict
                    result_json = json.dumps(result_dict, default=str)  # turn the dict into JSON format
                    return tool_response(content=result_json, tool_id=tool_call.id)
        return tool_response(content="No such tool in the registry", tool_id=tool_call.id)
