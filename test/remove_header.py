def remove_ss_tag_frequency_ascii(file_path):
    with open(file_path, "rb") as f:
        content = f.read()
    
    start_pattern = b'{"__metadata__"'
    end_pattern = b'"data_offsets":[316343024,316932848]}}'

    start_index = content.find(start_pattern)
    print(start_index)
    if start_index == -1:
        print("ss_tag_frequency field not found.")
        return
    
    end_index = content.find(end_pattern, start_index) + len(end_pattern)
    print(end_index)
    if end_index == -1:
        print("Could not find the end of ss_tag_frequency field.")
        return

    new_content = content[:start_index] + content[end_index:]
    
    with open(file_path+"_new.safetensors", "wb") as f:
        f.write(new_content)
    
    print("Successfully removed ss_tag_frequency from file.")

remove_ss_tag_frequency_ascii("hv24_v2.safetensors_new.safetensors")
