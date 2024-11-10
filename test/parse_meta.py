import json
import traceback

def validate_safetensors_metadata(file_path):
    try:
        with open(file_path, "rb") as f:
            metadata_len_bytes = f.read(8)
            metadata_len = int.from_bytes(metadata_len_bytes, byteorder='little')
            print(metadata_len)

            # 读取 metadata 部分
            metadata_bytes = f.read(metadata_len)
            buffer = f.read()

        try:
            metadata_str = metadata_bytes.decode("utf-8")
        except UnicodeDecodeError as e:
            return f"Error: Metadata is not a valid UTF-8 encoded string. Exception at line {e.__traceback__.tb_lineno}."

        with open("metadata.json", "w", encoding="utf-8") as json_file:
            json_file.write(metadata_str)

        if not metadata_str.startswith('{'):
            return "Error: Metadata does not start with '{'."

        try:
            metadata = json.loads(metadata_str)
        except json.JSONDecodeError as e:
            return f"Error: Metadata is not valid JSON. Exception at line {e.__traceback__.tb_lineno}."

        metadata_size = len(metadata_bytes)
        buffer_size = len(buffer)
        if metadata_size + 8 + buffer_size != metadata_len + 8 + buffer_size:
            return "Error: Metadata or buffer size is inconsistent with the header length."

        return "Metadata is valid."

    except Exception as e:
        error_info = traceback.format_exc()
        return f"An error occurred:\n{error_info}"

print(validate_safetensors_metadata("hv24_v2_header2.safetensors"))
