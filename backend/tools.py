# File: backend/tools.py

from langchain_core.tools import tool
import json # For handling potential JSON output if needed later

# Placeholder for where documents might be loaded or accessed
# In a real system, this might involve loading from a DB or file system
# For now, we'll simulate finding data.
SIMULATED_DOC_CONTENT = {
    "introduction": "This report details the findings...",
    "clinical_findings": "The patient presented with symptoms A, B, and C. Lab results showed X.",
    "patient_tables": "[Simulated Table Data: Patient Demographics]",
    "graphs": "[Simulated Graph/Chart: Figure 1 - Symptom Progression]",
    "summary": "The patient's condition improved following treatment.",
}

@tool
def extract_exact_text(section_name: str) -> str:
    """
    Extracts the exact text content for a specified section from the available medical documents.
    Use this tool when the user asks for a specific section like 'Introduction', 'Clinical Findings', etc.,
    and does NOT ask for a summary.
    """
    print(f"--- Tool: extract_exact_text called with section_name: {section_name} ---")
    # Normalize the section name for lookup (simple example)
    normalized_section = section_name.lower().replace(" ", "_")

    # Simulate finding the section in our placeholder content
    content = SIMULATED_DOC_CONTENT.get(normalized_section, None)

    if content:
        print(f"--- Tool: Found content for {section_name} ---")
        return content
    else:
        print(f"--- Tool: Section '{section_name}' not found ---")
        return f"Error: The section '{section_name}' could not be found in the documents."

@tool
def extract_table(table_description: str) -> str:
    """
    Extracts specific table data described by the user (e.g., 'patient demographics table', 'lab results table')
    from the medical documents.
    """
    print(f"--- Tool: extract_table called with table_description: {table_description} ---")
    # Simulate finding based on description - very basic for now
    if "patient" in table_description.lower() or "demographics" in table_description.lower():
         print(f"--- Tool: Found patient table ---")
         return SIMULATED_DOC_CONTENT.get("patient_tables", "Error: Patient table not found.")
    else:
        print(f"--- Tool: Table '{table_description}' not found ---")
        return f"Error: The table described as '{table_description}' could not be found."

@tool
def extract_image(image_description: str) -> str:
    """
    Extracts specific charts, graphs, or clinical figures described by the user (e.g., 'symptom progression chart', 'figure 1')
    from the medical documents.
    """
    print(f"--- Tool: extract_image called with image_description: {image_description} ---")
    # Simulate finding based on description - very basic for now
    if "graph" in image_description.lower() or "chart" in image_description.lower() or "figure" in image_description.lower():
        print(f"--- Tool: Found graph/figure ---")
        return SIMULATED_DOC_CONTENT.get("graphs", "Error: Graph/Chart not found.")
    else:
        print(f"--- Tool: Image '{image_description}' not found ---")
        return f"Error: The image described as '{image_description}' could not be found."

@tool
def generate_summary(section_to_summarize: str) -> str:
    """
    Generates a concise summary of the specified section (e.g., 'Clinical Findings', 'Introduction')
    from the medical documents. Use this ONLY when the user explicitly asks for a summary of a section.
    """
    print(f"--- Tool: generate_summary called for section: {section_to_summarize} ---")
    # Simulate finding the original text first
    normalized_section = section_to_summarize.lower().replace(" ", "_")
    original_content = SIMULATED_DOC_CONTENT.get(normalized_section, None)

    if original_content:
        # In a real system, you'd pass `original_content` to another LLM call for summarization.
        # For now, we'll just return a placeholder summary.
        print(f"--- Tool: Generating simulated summary for {section_to_summarize} ---")
        return f"[Simulated Summary of {section_to_summarize}: {original_content[:50]}...]" # Truncated original
    else:
        print(f"--- Tool: Section '{section_to_summarize}' not found for summarization ---")
        return f"Error: Cannot summarize section '{section_to_summarize}' as it was not found."

# List of all tools available
all_tools = [extract_exact_text, extract_table, extract_image, generate_summary]