def modify_header(file_path, output_file_path, new_header):
    new_header_bytes = new_header.to_bytes(8, byteorder='little')
    with open(file_path, "rb") as f:
        content = f.read()
    modified_content = new_header_bytes + content[8:]
    with open(output_file_path, "wb") as f:
        f.write(modified_content)
    print(f"Successfully modified the header and saved to {output_file_path}.")
modify_header("hv24_v2_trimed.safetensors", "hv24_v2_header.safetensors", 0x00022A3F)
