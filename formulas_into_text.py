import re
import config_api_key
from langchain_google_genai import ChatGoogleGenerativeAI
import random
import os

# Function to detect LaTeX formulas in a md file
def extract_latex_segments(md_file_path,content):
    # I tried to use findall $...$, but it brings errors when
    # considering cases like "$5000" and "\$200".
    first_segment = content.split('$')
    # Filter only the segments that contain the "\" or "=" character,
    # which indicates LaTeX segments
    return [segment for segment in first_segment if ("\\" or "=") in segment]

# Function to detect LaTeX tables in a md file
def extract_table_segments(md_file_path, content):
    table_segments = re.findall(r'<table.*?>.*?</table>', content, re.DOTALL)
    
    return [segment for segment in table_segments if segment.strip()]

llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0)   

# Sends the latex segments to the llm to compact them
def compact_latex(latex_texts):
    try:
        prompt = r"""Compact into plain text the following list of mathematical expressions in LaTeX.
        The expressions are delimited by "i) expression<end>" where i is a number.
        Even if each line within the expression defines a different calculation, include everything in the same compacted form.
        If two or more expressions seem connected, treat them as separate.
        If an expression contains "\\", do not consider it as two or more expressions.
        At the end of each compacted form, always include <end> except for the last element.
        If there's text involded keep it as it is.

        Example:
        If the list is
        "1) d_1,\\ldots,d_(i-1)<end>2) d_(i+1),\\ldots,d_p<end>"
        The result should be:
        "d₁, …, dᵢ₋₁<end>dᵢ₊₁, …, dₚ"

        Important: The number of compacted expressions must match the number of input expressions.
        For example, if 5 expressions are provided, 5 compacted forms must be returned.
        """
        # Another example:
        # If the list is
        # "
        # 1) \\begin{aligned}\nE(Y_{0i})&=40 \\\\\n&=60-20\\end{aligned}\\\\\n&=20*2
        # 2) 40=20+20
        # "
        # The result should be: "E(Y₀ᵢ)&=40\n&=60-20\n&=20*2<end>40=20+20"
        prompt = prompt + f"""

        List to compact: {latex_texts}"""

        response = llm.invoke(prompt)
        response_content = dict(response)['content']
        return response_content
    except Exception as e:
        print(f"Error processing the LaTeX segments: {e}")
        return latex_texts

# Sends a single latex segment to the llm to compact it
def compact_latex_unit(latex_text):
    try:
        prompt = r"""Compact the following mathematical expression in LaTeX into plain text.
        At the end of the compacted form, include "<end>".
        If there's text involded keep it as it is.

        Example:
        If the input is:
        "1) d_1,\\ldots,d_(i-1),d_(i+1),\\ldots,d_p<end>"
        The result should be:
        "d₁, …, dᵢ₋₁,dᵢ₊₁, …, dₚ<end>"
        """
        prompt = prompt + f"""

        List to compact: {latex_text}"""

        response = llm.invoke(prompt)
        response_content = dict(response)['content']
        return response_content
    except Exception as e:
        print(f"Error processing the LaTeX segment: {e}")
        return latex_text

# Sends tables to the llm to compact them
def compact_tables(tables):
    try:
        prompt = f"""Compact the following tables into plain text using '|'.
        If there is a header, keep the column names.
        Tables: {tables}.

        Only respond with the direct compacted form.
        At the end of each compacted table, include '<end>''."""

        response = llm.invoke(prompt)
        response_content = dict(response)['content']
        return response_content.rstrip("\n\n")
    except Exception as e:
        print(f"Error processing the tables: {e}")
        return tables

# Main function to read the md files and extract the latex segments and the table
# to finally compact them.
def process_md_file(md_file_path, output_file_path):
    # Read the md file
    with open(md_file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Replace some characters in order to compact properly
    content = content.replace('\\\\','\n')
    # Extract the latex segment and the tables
    latex_segments = extract_latex_segments(md_file_path, content)
    table_segments = extract_table_segments(md_file_path, content)
    
    # Count the total number of requests
    count = 0

    # Multiple tables are gonna be passed in a single text
    text = f'{table_segments[0]}\n'
    table_list_to_request = [table_segments[0]]

    for i, table in enumerate(table_segments, start=1):
        # Gemini has an output token limit of approximately 8000.
        # Set a threshold of 1000 characters per request.
        if (len(text) + len(table) > 1000) or (i == len(table_segments)-1):
            # If it is the last element then add it to the table to request
            if i == len(table_segments)-1:
                table_list_to_request.append(table)

            # Now request the compactation
            compacted = compact_tables(text).split("<end>")

            # If the last element is an empty string remove it
            if compacted[-1] == '':
                compacted.pop()  # Delete the last element
            
            # If the compacted list length is not equal to the table_list_to_request
            # then compact each table in a individual request
            if len(table_list_to_request) < len(compacted) or len(table_list_to_request) > len(compacted):
                compacted = []
                for table_to_request in table_list_to_request:
                    compacted.append(compact_tables(f"{table_to_request}").rstrip('\n').split('<end>')[0])
                    # Count a request done
                    count += 1
                # Print a random result to see if it is well done
                n = 1
                indices = random.sample(range(len(table_list_to_request)), n)
                print('List:', [table_list_to_request[i] for i in indices])
                print('\n\nCompated list:', [compacted[i] for i in indices], '\n\n')

            # Only if the compacted list is equal in elements to the table_list_to_request
            if len(table_list_to_request) == len(compacted):
                for i in range(len(table_list_to_request)):
                    content = content.replace(f"{table_list_to_request[i]}", f"{compacted[i]}")
            # Count a request done
            count += 1
            # Restart the values with this new table that didn't enter to this request
            text = f'{table}\n'
            table_list_to_request = [table]
        
        # If the len of the request less than 4000 and it isn't the last element
        else:
            text += f'{table}\n'
            table_list_to_request.append(table)

    # Now with the latex formulas
    latex_list_to_request = [latex_segments[0]]
    # Length of the total request
    len_to_request = len(latex_segments[0])
    # By randomizing the list, I ensure that the LLM does not detect connections between segments
    # and merges them when I don't want them to be merged.
    random.shuffle(latex_segments)

    for i, latex in enumerate(latex_segments, start=1):
        # Gemini has an output token limit of approximately 8000.
        # The threshold needs to be adjusted so the LLM can understand the entire message
        # and act efficiently. I propose a threshold of 1000.
        # The downside is that it increases the number of requests choosing a low value
        if (len_to_request + len(latex) > 1000) or (i == len(latex_segments)-1):
            # If it is the last element add it to the request
            if i == len(latex_segments)-1:
                latex_list_to_request.append(latex)
            
            # Now request the compactation
            result = "".join([f"{i + 1}) {item}<end>" for i, item in enumerate(latex_list_to_request)])
            compacted = compact_latex(result)
            compacted_list = compacted.rstrip('\n').split("<end>")

            # Count a request done
            count += 1
            
            # Sometimes it happens that the last element of the compacted list
            # is an empty string
            if len(latex_list_to_request) < len(compacted_list):
                if compacted_list[-1] == '':
                    compacted_list.pop()  # Delete the last element

            # If it doesn't match the dimensions then do the request of each element individually
            if len(latex_list_to_request) < len(compacted_list) or len(latex_list_to_request) > len(compacted_list):
                compacted_list = []
                for latex_to_request in latex_list_to_request:
                    compacted_list.append(compact_latex_unit(f"{latex_to_request}").rstrip('\n').split('<end>')[0])
                    # Count a request done
                    count += 1
                # Print some results to see if it is well done
                if len(latex_list_to_request) > 5:
                    n = 5
                else:
                    n = len(latex_list_to_request)
                indices = random.sample(range(len(latex_list_to_request)), n)
                print('List:', [latex_list_to_request[i] for i in indices])
                print('\n\nCompated list:', [compacted_list[i] for i in indices], '\n\n')

            # Now if it does match the dimensions then replace
            if len(latex_list_to_request) == len(compacted_list):
                for i in range(len(latex_list_to_request)):
                    content = content.replace(f"$${latex_list_to_request[i]}$$",
                                              f"{compacted_list[i]}").replace(f"${latex_list_to_request[i]}$",
                                                                              f"{compacted_list[i]}").replace("ï¼Œ", ",")

            # Restart the value with the latex formula that
            # hasn't been included in this request
            len_to_request = len(latex)
            latex_list_to_request = [latex]

        # If it isn't the last element and the request is less than 3000 characters
        else:
            latex_list_to_request.append(latex)
            len_to_request += len(latex)

    print('Total requests done:',count)

    # Now save the file with all the compactations done
    with open(output_file_path, 'w', encoding='utf-8') as file:
        file.write(content)

# Directory of the md files to be compacted
md_directory = './md/merged_files'

# Compact each md file in the folder
for filename in os.listdir(md_directory):
    if filename.endswith(".md"):
        process_md_file(md_file_path = md_directory + "/" + filename,
                        output_file_path = f"final_md/{filename}")
        print(f"File {filename} processed successfully")
