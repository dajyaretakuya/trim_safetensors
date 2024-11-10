import json
import struct
import sys

def load_safetensors_file(filename):
    with open(filename, "rb") as f:
        header_length_bytes = f.read(8)
        header_length = struct.unpack("<Q", header_length_bytes)[0]
        header_bytes = f.read(header_length)
        header = json.loads(header_bytes.decode("utf-8"))
    return header, header_length

def show_metadata_lengths(header):
    metadata = header.get("__metadata__", {})
    if not metadata:
        print("No __metadata__ field in the file")
        return
    
    sorted_metadata = sorted(metadata.items(), key=lambda item: len(str(item[1])), reverse=True)
    for key, value in sorted_metadata:
        print(f"{key} - Length: {len(str(value))}")

def save_trimmed_safetensors_file(filename, output_filename, fields_to_delete):
    header, header_length = load_safetensors_file(filename)
    
    if "__metadata__" in header:
        for key in fields_to_delete:
            header["__metadata__"].pop(key, None)

    new_header_bytes = json.dumps(header, separators=(',', ':')).encode("utf-8")
    new_header_length = len(new_header_bytes)
    offset_delta = new_header_length - header_length

    for tensor_info in header.values():
        if isinstance(tensor_info, dict) and "data_offsets" in tensor_info:
            start_offset, end_offset = tensor_info["data_offsets"]
            tensor_info["data_offsets"] = [start_offset + offset_delta, end_offset + offset_delta]

    with open(output_filename, "wb") as f:
        f.write(struct.pack("<Q", new_header_length))
        f.write(new_header_bytes)
        
        with open(filename, "rb") as original_file:
            original_file.seek(8 + header_length)
            bin_data = original_file.read()
            f.write(bin_data)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage:")
        print("  To delete specific metadata fields: python trim_sft.py <filename> <output_filename> <fields_to_delete>...")
        print("  To show metadata field lengths: python trim_sft.py <filename> show_metadata")
        sys.exit(1)
    
    filename = sys.argv[1]

    if sys.argv[2] == "show_metadata":
        header, _ = load_safetensors_file(filename)
        show_metadata_lengths(header)
    else:
        output_filename = sys.argv[2]
        fields_to_delete = sys.argv[3:]
        save_trimmed_safetensors_file(filename, output_filename, fields_to_delete)
        print(f"File saved as: {output_filename}")
