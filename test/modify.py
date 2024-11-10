import traceback

def process_safetensors_metadata(file_path, output_file_path):
    try:
        with open(file_path, "rb") as f:
            metadata_len_bytes = f.read(8)
            metadata_len = int.from_bytes(metadata_len_bytes, byteorder='little')
            metadata_bytes = f.read(metadata_len)
            remaining_content = f.read()

        corrected_metadata_bytes = bytearray()
        i = 0
        while i < len(metadata_bytes):
            if i < len(metadata_bytes) - 1 and metadata_bytes[i] == ord(',') and metadata_bytes[i + 1] == ord(','):
                corrected_metadata_bytes.append(ord(','))
                i += 2
                metadata_len -= 1
            else:
                corrected_metadata_bytes.append(metadata_bytes[i])
                i += 1

        new_metadata_len_bytes = metadata_len.to_bytes(8, byteorder='little')
        final_content = new_metadata_len_bytes + corrected_metadata_bytes + remaining_content

        with open(output_file_path, "wb") as f:
            f.write(final_content)

        print(f"Metadata processed and saved to {output_file_path} with updated length.")

    except Exception as e:
        error_info = traceback.format_exc()
        print(f"An error occurred:\n{error_info}")

process_safetensors_metadata("hv24_v2_header.safetensors", "hv24_v2_header2.safetensors")
