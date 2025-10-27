
import os
import shutil
import json
from typing import List, Dict, TypedDict, Annotated, Union, Any
import operator
import pprint
from langchain_core.messages import BaseMessage, FunctionMessage, HumanMessage, ToolMessage
from langchain_community.chat_models import ChatOllama
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor, ToolInvocation
import rag_module as rag

@tool
def extract_exact_text(section_title: str) -> str:
    print(f"🛠️ TOOL CALLED: extract_exact_text for section '{section_title}'")
    try:
        retriever = rag.get_rag_chain().context
        query = f"Retrieve the full text content found under the section titled or closely related to '{section_title}' in the NAFLD documents."
        docs = retriever.invoke(query)
        combined_text = "\n\n".join([doc.page_content for doc in docs])
        if not combined_text:
            return f"No specific content found for section '{section_title}'. Verify the section title exists in the documents."
        print(f"  -> Extracted text length: {len(combined_text)}")
        return combined_text[:4000]
    except Exception as e:
        print(f"  ❌ Error in extract_exact_text: {e}")
        return f"Error extracting text for section '{section_title}': {e}"

@tool
def extract_figures_tables(figure_or_table_description: str) -> List[Dict[str, Any]]:
    print(f"🛠️ TOOL CALLED: extract_figures_tables for '{figure_or_table_description}'")
    results = []
    desc_lower = figure_or_table_description.lower()
    base_data_path = os.path.abspath(rag.DATA_PATH)
    if "flowchart" in desc_lower and "inclusion" in desc_lower:
        img_path = os.path.join(base_data_path, "FlowChart.png")
        if os.path.exists(img_path):
            print(f"  -> Found image: {img_path}")
            results.append({"type": "image", "path": img_path, "caption": "Study Inclusion and Screening Flowchart (PRISMA)"})
        else:
            print(f"  -> Image not found: FlowChart.png")
            results.append({"type": "text", "content": f"Image 'FlowChart.png' not found at expected location ({img_path})."})
    elif "city-wise" in desc_lower and ("nafld" in desc_lower or "prevalence" in desc_lower):
         img_path = os.path.join(base_data_path, "city-wise-nafld.png")
         if os.path.exists(img_path):
              print(f"  -> Found image: {img_path}")
              results.append({"type": "image", "path": img_path, "caption": "State-wise NAFLD Prevalence Data in India"})
         else:
              print(f"  -> Image not found: city-wise-nafld.png")
              results.append({"type": "text", "content": f"Image 'city-wise-nafld.png' not found at expected location ({img_path})."})
    elif "table 1" in desc_lower and ("publication" in desc_lower or "statistic" in desc_lower):
         print("  -> Extracting placeholder data for Table 1")
         table_data = [
             ["Region/Keyword", "Metric", "2001-2012", "2013-2022", "2001-2022"],
             ["India", "Total papers", "126", "730", "856"],
             ["", "Total citations", "5426", "17,039", "22,465"],
             ["", "CPP", "43.06", "23.34", "26.44"],
             ["Select Subcontinent", "Total papers", "20", "199", "219"],
             ["", "Total citations", "1192", "3755", "4947"],
             ["", "CPP", "59.60", "18.87", "22.59"],
             ["Indian Subcontinent", "Total papers", "145", "908", "1053"],
             ["", "Total citations", "5784", "18,911", "24,695"],
             ["", "CPP", "39.89", "20.83", "23.45"]
         ]
         results.append({"type": "table", "data": table_data, "caption": "Table 1: Publication and Citation Statistics from Indian Subcontinent"})
    if not results:
        print(f"  -> No specific figure/table found matching '{figure_or_table_description}'")
        results.append({"type": "text", "content": f"Could not find a specific figure or table matching the description: '{figure_or_table_description}'. Please check the documents or refine the description."})
    return results

@tool
def generate_summary(topic: str = "Overall Summary based on provided NAFLD documents") -> str:
    print(f"🛠️ TOOL CALLED: generate_summary for '{topic}'")
    try:
        rag_chain = rag.get_rag_chain()
        query = f"Based ONLY on the provided context documents about NAFLD, generate a concise, professional summary covering the key aspects of '{topic}'. If the topic is general, focus on prevalence, risk factors, progression, assessment, and key research findings mentioned."
        summary = rag_chain.invoke(query)
        summary_text = str(summary).strip() if summary else ""
        print(f"  -> Generated summary length: {len(summary_text)}")
        return summary_text if summary_text else "Summary could not be generated from the available context."
    except Exception as e:
        print(f"  ❌ Error in generate_summary: {e}")
        return f"Error generating summary for '{topic}': {e}"

tools = [extract_exact_text, extract_figures_tables, generate_summary]
tool_executor = ToolExecutor(tools)
llm = ChatOllama(model="llama3:8b", format="json", temperature=0.1).bind_tools(tools)

class ReportState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]

def agent_node(state: ReportState):
    print("--- 🧠 NODE: Agent ---")
    response = llm.invoke(state['messages'])
    return {"messages": [response]}

def tool_node(state: ReportState):
    print("--- 🛠️ NODE: Tool Executor ---")
    last_message = state['messages'][-1]
    tool_calls = last_message.tool_calls
    tool_messages = []
    if tool_calls:
        print(f"  Attempting Tool Calls: {[(tc['name'], tc['args']) for tc in tool_calls]}")
        responses = tool_executor.batch(
            [ToolInvocation(tool=tc["name"], tool_input=tc["args"]) for tc in tool_calls],
            return_exceptions=True
        )
        for tc, resp in zip(tool_calls, responses):
            if isinstance(resp, Exception):
                content_str = f"Error executing tool {tc['name']}: {type(resp).__name__} - {resp}"
                print(f"    Tool Error: {content_str}")
            elif isinstance(resp, (str, list, dict)):
                 try:
                      content_str = json.dumps(resp)
                 except TypeError as json_err:
                      content_str = f"Tool {tc['name']} returned non-JSON-serializable data: {type(resp).__name__} - {json_err}"
                      print(f"    Warning: {content_str}")
            else:
                 content_str = str(resp)
            tool_messages.append(ToolMessage(content=content_str, tool_call_id=tc['id']))
        print(f"  Tool Responses generated.")
    else:
        print("  No tool calls requested by agent.")
    return {"messages": tool_messages}

def should_continue(state: ReportState):
    last_message = state['messages'][-1]
    if not last_message.tool_calls:
        print("--- 🚦 DECISION: End (No tool calls) ---")
        return END
    else:
        print("--- 🚦 DECISION: Continue (Execute Tool) ---")
        return "call_tool"

workflow = StateGraph(ReportState)
workflow.add_node("agent", agent_node)
workflow.add_node("call_tool", tool_node)
workflow.set_entry_point("agent")
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {END: END, "call_tool": "call_tool"}
)
workflow.add_edge("call_tool", "agent")
graph_app = workflow.compile()

def run_graph(user_request: str) -> Dict[str, List[Dict[str, Any]]]:
    print(f"\n--- 🚀 Running Graph for User Request: '{user_request}' ---")
    initial_prompt = f"""You are a meticulous medical report generation assistant specializing in Non-alcoholic Fatty Liver Disease (NAFLD). Your task is to create a structured report in JSON format based on the provided internal documents (research papers, guidelines etc.) and the user's specific request: '{user_request}'.

Available tools and their usage:
- `extract_exact_text(section_title: str)`: Extracts verbatim text for specific document sections like 'Introduction', 'Epidemiology', 'Risk Factors', 'Assessment', 'Natural History', 'Definitions', 'Prevalence', 'Incidence', 'Conclusion', 'Research Landscape (Indian Subcontinent)'. Provide the *exact* section title found in the documents if possible. Use this for most text-based sections unless a summary is required.
- `extract_figures_tables(description: str)`: Extracts specific visuals/tables based on their description (e.g., 'Flowchart of study inclusion', 'Table 1: Publication Statistics', 'Figure 2: Prevalence Map', 'city-wise NAFLD prevalence data', 'Table 2', 'Figure 3'). Provide a clear, unique description found in the documents or captions.
- `generate_summary(topic: str)`: Generates a concise summary based *only* on the provided document context. Use this *exclusively* if the user explicitly requests a 'Summary' section or a summary of a specific topic (provide that topic). Default topic is 'Overall Summary of NAFLD Documents'.

Your Process:
1.  **Analyze Request:** Carefully examine the user request: '{user_request}'. Identify *all* specific sections, figures, tables, or topics mentioned.
2.  **Determine Sections:** Based on the request analysis, decide the final list of sections for the report. If the request is generic (e.g., "generate a report on NAFLD"), use a comprehensive set of default sections relevant to the documents, such as: "Executive Summary" (use generate_summary), "Introduction & Definitions", "Epidemiology: Prevalence and Incidence", "Risk Factors", "Natural History and Progression", "Diagnosis and Assessment Methods", "Key Figures and Tables" (use extract_figures_tables multiple times), "Research Landscape (Indian Subcontinent)", "Conclusion".
3.  **Plan Tool Calls:** Create a sequence of tool calls needed to gather content for *each* required section.
4.  **Execute Tools Sequentially:** Call the *first* tool needed. Wait for the result. Then call the *second* tool needed, wait for its result, and so on. Do this until you have gathered content for all planned sections.
5.  **Compile Final JSON:** After ALL necessary tool calls are complete and you have received their responses (which will be JSON strings or simple strings), assemble the final report data. Your ABSOLUTE FINAL output message MUST be ONLY the structured JSON object representing the complete report_data. It MUST follow this format precisely:
    ```json
    {{
        "Section Title 1": [{{"type": "text", "content": "..."}}],
        "Section Title 2": [
            {{"type": "image", "path": "...", "caption": "..."}},
            {{"type": "table", "data": [[...], [...]], "caption": "..."}}
        ],
        "Section Title 3": [{{"type": "text", "content": "..."}}]
    }}
    ```
    - Ensure correct JSON syntax (double quotes for keys and strings, commas between elements).
    - Map the content from the tool responses correctly into the `content`, `path`, `data`, and `caption` fields within the list for each section.
    - Do NOT include any conversational text, explanations, apologies, status updates, or the raw tool call/response JSON strings in your final output message. Just the compiled report data JSON object.
"""
    final_state = None
    report_data = {}
    max_iterations = 8
    iterations = 0
    try:
        final_state = graph_app.invoke(
            {"messages": [HumanMessage(content=initial_prompt)]},
        )
        last_message = final_state['messages'][-1] if final_state and final_state.get('messages') else None
        if last_message and isinstance(last_message, BaseMessage) and not last_message.tool_calls:
            last_message_content = last_message.content
            print(f"--- Agent Final Output Attempt ---\n{last_message_content}\n------------------------------")
            cleaned_content = last_message_content.strip()
            if cleaned_content.startswith("```json"): cleaned_content = cleaned_content[7:]
            if cleaned_content.startswith("```"): cleaned_content = cleaned_content[3:]
            if cleaned_content.endswith("```"): cleaned_content = cleaned_content[:-3]
            cleaned_content = cleaned_content.strip()
            report_data = json.loads(cleaned_content)
            if not isinstance(report_data, dict):
                raise ValueError("LLM final output parsed as JSON but is not a dictionary.")
            print("--- ✅ Successfully Parsed Structured Report Data from LLM ---")
        else:
             raise ValueError("Agent did not provide a final response without tool calls.")
    except (json.JSONDecodeError, ValueError, IndexError, AttributeError, TypeError, KeyError) as e:
        print(f"--- ⚠️ ERROR: Could not reliably parse structured JSON from LLM's final message: {e} ---")
        print("--- Attempting Fallback: Reconstructing from Tool Messages (Less Reliable) ---")
        report_data = {}
        section_order = []
        if final_state and 'messages' in final_state:
            tool_call_map = {}
            for msg in final_state['messages']:
                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                    for tc in msg.tool_calls:
                        tool_call_map[tc['id']] = {'name': tc['name'], 'args': tc['args']}
            for msg in final_state['messages']:
                if isinstance(msg, ToolMessage) and msg.tool_call_id in tool_call_map:
                    try:
                        call_info = tool_call_map[msg.tool_call_id]
                        tool_name = call_info['name']
                        tool_args = call_info['args']
                        try:
                             content_data = json.loads(msg.content)
                        except (json.JSONDecodeError, TypeError):
                             content_data = msg.content
                        section_title = tool_args.get('section_title') or tool_args.get('topic') or tool_args.get('description') or f"Extracted_Content_{len(report_data)+1}"
                        if section_title not in section_order: section_order.append(section_title)
                        if tool_name in ['extract_exact_text', 'generate_summary']:
                             report_data.setdefault(section_title, []).append({"type": "text", "content": str(content_data)})
                        elif tool_name == 'extract_figures_tables':
                             if isinstance(content_data, list):
                                 report_data.setdefault(section_title, []).extend(content_data)
                             else:
                                  report_data.setdefault(section_title, []).append({"type": "text", "content": f"Figure/Table tool ({section_title}) returned unexpected data: {content_data}"})
                    except Exception as tool_parse_e:
                        print(f"  Error processing tool message content ({msg.tool_call_id}): {tool_parse_e}")
            ordered_data = {sec: report_data[sec] for sec in section_order if sec in report_data}
            ordered_data.update({sec: data for sec, data in report_data.items() if sec not in ordered_data})
            report_data = ordered_data
            if report_data: print("--- Reconstructed Report Data from Tool Messages ---")
        if not report_data:
             raw_output = final_state['messages'][-1].content if final_state and final_state.get('messages') else "Agent failed."
             report_data = {"Fatal Error": [{"type": "text", "content": f"Could not generate or parse structured report. Last agent output: {raw_output}"}]}
             print("--- ❌ Failed to Generate/Parse Report Data ---")
    print(f"\n---  Final Report Data Structure to Generate PDF ---")
    pprint.pprint(report_data)
    print("-------------------------------------------------------")
    return report_data

