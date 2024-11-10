import markdown
from weasyprint import HTML

def lingu_struct_to_human_readable(lingu_struct_data, key_mapping):
    """Convert LinguStruct JSON data to a human-readable format."""
    human_readable = {}
    for key, value in lingu_struct_data.items():
        human_key = key_mapping.get(key, key)
        if isinstance(value, dict):
            human_readable[human_key] = lingu_struct_to_human_readable(value, key_mapping)
        elif isinstance(value, list):
            human_readable[human_key] = [
                lingu_struct_to_human_readable(item, key_mapping) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            human_readable[human_key] = value
    return human_readable

def human_readable_to_lingu_struct(human_readable_data, key_mapping_reverse):
    """Convert human-readable format back to LinguStruct JSON."""
    lingu_struct = {}
    for key, value in human_readable_data.items():
        lingu_key = key_mapping_reverse.get(key, key)
        if isinstance(value, dict):
            lingu_struct[lingu_key] = human_readable_to_lingu_struct(value, key_mapping_reverse)
        elif isinstance(value, list):
            lingu_struct[lingu_key] = [
                human_readable_to_lingu_struct(item, key_mapping_reverse) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            lingu_struct[lingu_key] = value
    return lingu_struct

def lingu_struct_to_markdown(lingu_struct_data, key_mapping):
    """Convert LinguStruct JSON to Markdown."""
    human_readable = lingu_struct_to_human_readable(lingu_struct_data, key_mapping)
    return human_readable_to_markdown(human_readable)

def human_readable_to_markdown(human_readable_data, indent=0):
    """Convert human-readable format to Markdown."""
    markdown_text = ""
    for key, value in human_readable_data.items():
        if isinstance(value, dict):
            markdown_text += f"{'  ' * indent}- **{key}**:\n"
            markdown_text += human_readable_to_markdown(value, indent + 1)
        elif isinstance(value, list):
            markdown_text += f"{'  ' * indent}- **{key}**:\n"
            for item in value:
                if isinstance(item, dict):
                    markdown_text += human_readable_to_markdown(item, indent + 1)
                else:
                    markdown_text += f"{'  ' * (indent + 1)}- {item}\n"
        else:
            markdown_text += f"{'  ' * indent}- **{key}**: {value}\n"
    return markdown_text

def markdown_to_human_readable(markdown_text, key_mapping_reverse):
    """Convert Markdown back to a human-readable format."""
    human_readable = {}
    lines = markdown_text.strip().splitlines()
    current_human_key = None
    stack = [human_readable]

    for line in lines:
        stripped_line = line.lstrip()
        indent = (len(line) - len(stripped_line)) // 2  # 2 spaces per indent level

        # Adjust the stack based on current indent
        while indent + 1 < len(stack):
            stack.pop()

        if stripped_line.startswith("- **") and stripped_line.endswith("**:"):
            # New key
            key = stripped_line[4:-3].strip()
            human_key = key_mapping_reverse.get(key, key)
            stack[-1][human_key] = {}
            stack.append(stack[-1][human_key])
        elif stripped_line.startswith("- "):
            # List item
            item = stripped_line[2:].strip()
            if isinstance(stack[-1], list):
                stack[-1].append(item)
            else:
                # Convert current dict key to list
                last_key = list(stack[-1].keys())[-1]
                stack[-1][last_key] = [item]
                stack.append(stack[-1][last_key])
        elif stripped_line.startswith("**") and stripped_line.endswith("**:"):
            # Handle bolded keys without list
            key = stripped_line[2:-3].strip()
            human_key = key_mapping_reverse.get(key, key)
            stack[-1][human_key] = {}
            stack.append(stack[-1][human_key])
        else:
            # Regular key-value
            if ": " in stripped_line:
                key, value = stripped_line.split(": ", 1)
                human_key = key_mapping_reverse.get(key.strip("**"), key.strip("**"))
                stack[-1][human_key] = value
            else:
                # Continuation of previous value
                pass  # Implement as needed

    # Clean up any remaining empty dictionaries
    def clean_empty(d):
        if isinstance(d, dict):
            return {k: clean_empty(v) for k, v in d.items() if v}
        elif isinstance(d, list):
            return [clean_empty(i) for i in d]
        else:
            return d

    return clean_empty(human_readable)

def markdown_to_pdf(markdown_text, output_path='output.pdf'):
    """Convert Markdown to PDF."""
    html = markdown_to_html(markdown_text)
    return convert_html_to_pdf(html)

def markdown_to_html(markdown_text):
    """Convert Markdown to HTML."""
    return markdown.markdown(markdown_text)

def convert_html_to_pdf(html_content):
    """Convert HTML content to PDF binary data."""
    pdf = HTML(string=html_content).write_pdf()
    return pdf
