import sys
import re

def read_file(filename):
    """
    Read the content of the file.
    
    This function opens the specified file in UTF-8 encoding and reads its entire content into a string.
    It handles the input file which is expected to be a text file containing the raw eBook content.
    
    Args:
        filename (str): The name of the file to read (e.g., "The Ethic.txt").
    
    Returns:
        str: The full content of the file as a string.
    """
    with open(filename, 'r', encoding='utf-8') as f:
        return f.read()

def extract_main_content(text):
    """
    Extract the main content between Gutenberg start and end markers.
    
    This function locates the standard Project Gutenberg start and end markers in the text and extracts
    the content between them, excluding the header, footer, and license information. If markers are not
    found, it returns the entire text to avoid data loss.
    
    Args:
        text (str): The raw text content of the file.
    
    Returns:
        str: The extracted main content of the eBook.
    """
    start_marker = "*** START OF THIS PROJECT GUTENBERG EBOOK THE ETHICS ***"
    end_marker = "*** END OF THIS PROJECT GUTENBERG EBOOK THE ETHICS ***"
    
    start_idx = text.find(start_marker)
    if start_idx == -1:
        return text  # Return full text if start marker not found
    
    start_idx += len(start_marker)
    
    end_idx = text.find(end_marker, start_idx)
    if end_idx == -1:
        return text[start_idx:]  # Return from start to end if end marker not found
    
    return text[start_idx:end_idx].strip()

def clean_and_standardize(content):
    """
    Clean, organize, standardize, and format the text for readability.
    
    This function performs several cleaning operations:
    - Removes production notes (e.g., "Produced by..." lines).
    - Normalizes whitespace: strips leading/trailing spaces per line, reduces multiple newlines to single.
    - Organizes structure by inserting blank lines before key sections (e.g., PART, DEFINITIONS, PROP., Proof., etc.) for better readability.
    - Preserves footnotes and endnotes as they are part of the content.
    - Handles potential truncations or artifacts (e.g., "(truncated ...)") by removing them if present.
    - Standardizes section headings to start on new paragraphs.
    
    The goal is to make the text more readable in plain text format while preserving the philosophical structure.
    
    Args:
        content (str): The extracted main content to clean.
    
    Returns:
        str: The cleaned and formatted text.
    """
    # Remove production notes
    content = re.sub(r'Produced by Tom Sharpe\. HTML version by Al Haines\.', '', content)
    
    # Remove any truncation artifacts if present
    content = re.sub(r'\.\.\.\(truncated \d+ characters\)\.\.\.', '', content)
    
    # Split into lines for processing
    lines = content.splitlines()
    
    # Strip leading/trailing whitespace from each line
    lines = [line.strip() for line in lines]
    
    # Join back and normalize multiple newlines
    content = '\n'.join(line for line in lines if line)  # Remove empty lines temporarily
    content = re.sub(r'\n+', '\n', content)
    
    # Define patterns for sections to insert blank lines before them for organization
    section_patterns = [
        r'(PART [IVX]+\.)',  # PART I., PART II., etc.
        r'(DEFINITIONS\.)',
        r'(AXIOMS\.)',
        r'(PROPOSITIONS\.)',
        r'(PROP\. [IVXLCDM]+\.)',  # PROP. I., PROP. II., etc.
        r'(Proof\.—)',
        r'(Note\.—)',
        r'(Note I\.—)',
        r'(Note II\.—)',
        r'(Corollary\.—)',
        r'(Corollary I\.—)',
        r'(Corollary II\.—)',
        r'(Explanation—)',
        r'(End of the Ethics by Benedict de Spinoza)'
    ]
    
    # Insert double newlines before each section pattern for separation
    for pattern in section_patterns:
        content = re.sub(r'(' + pattern + r')', r'\n\n\1', content)
    
    # Ensure footnotes/endnotes are kept but separated
    content = re.sub(r'(\[\d+\])', r'\n\1', content)  # Start footnotes on new lines
    
    # Final normalization: reduce any excessive newlines
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    return content.strip()

def write_output(original_filename, cleaned_content):
    """
    Write the cleaned content to a new file in the same folder.
    
    This function creates a new file named "cleaned_<original_filename>" and writes the processed content to it.
    It prints a confirmation message upon success.
    
    Args:
        original_filename (str): The original filename (used to generate output name).
        cleaned_content (str): The cleaned text to write.
    """
    output_filename = 'cleaned_' + original_filename
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(cleaned_content)
    print(f"Cleaned file written to: {output_filename}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <filename.txt>")
        sys.exit(1)
    
    filename = sys.argv[1]
    raw_text = read_file(filename)
    main_content = extract_main_content(raw_text)
    cleaned_text = clean_and_standardize(main_content)
    write_output(filename, cleaned_text)
