# import csv
# import math
# import os
# import shutil
# from pathlib import Path
# from collections import Counter
# from typing import Dict

# from fastapi import FastAPI, UploadFile, File, HTTPException
# from fastapi.concurrency import run_in_threadpool
# # Import the CORS middleware and FileResponse
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import FileResponse
# import uvicorn

# # --- FastAPI App Initialization ---
# app = FastAPI(
#     title="Item Analysis API",
#     description="Upload student responses and an answer key to perform automated item analysis.",
# )

# # --- CORS (Cross-Origin Resource Sharing) Configuration ---
# origins = [
#     "http://localhost",
#     "http://localhost:3000", # Default React dev server port
#     "http://localhost:5173", # Default Vite dev server port
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"], # Allows all methods (GET, POST, etc.)
#     allow_headers=["*"], # Allows all headers
# )


# # --- Directory Setup for Storing Uploaded Files ---
# INPUT_DIR = Path("input_file")
# INPUT_DIR.mkdir(exist_ok=True)


# # --- Helper Function to Manage Batch Directories ---
# def get_next_batch_path() -> Path:
#     """
#     Determines the next batch directory path (e.g., input_file/batch_1, input_file/batch_2).
#     """
#     existing_batches = [d for d in INPUT_DIR.iterdir() if d.is_dir() and d.name.startswith("batch_")]
    
#     if not existing_batches:
#         next_batch_num = 1
#     else:
#         max_num = 0
#         for batch_dir in existing_batches:
#             try:
#                 num = int(batch_dir.name.split("_")[1])
#                 if num > max_num:
#                     max_num = num
#             except (IndexError, ValueError):
#                 continue
#         next_batch_num = max_num + 1
    
#     batch_path = INPUT_DIR / f"batch_{next_batch_num}"
#     batch_path.mkdir(exist_ok=True)
#     return batch_path


# # --- Core Analysis Functions ---

# def calculate_std_dev(data: list) -> float:
#     """Calculates the population standard deviation for a list of numbers."""
#     n = len(data)
#     if n < 2:
#         return 0.0
#     mean = sum(data) / n
#     variance = sum((x - mean) ** 2 for x in data) / n
#     return math.sqrt(variance)

# def load_correct_answers(filename: str) -> Dict[str, str]:
#     """Reads the answer key CSV file and returns a dictionary of correct answers."""
#     correct_answers = {}
#     try:
#         with open(filename, mode='r', newline='', encoding='utf-8') as answer_file:
#             reader = csv.reader(answer_file)
#             try:
#                 first_row = next(reader)
#                 if len(first_row) >= 2 and not (len(first_row[1]) > 1 or first_row[1].islower()):
#                     correct_answers[first_row[0]] = first_row[1]
#             except StopIteration:
#                 return {} # File is empty
            
#             # Process the rest of the file
#             for row in reader:
#                 if len(row) == 2:
#                     question_id, correct_answer = row
#                     correct_answers[question_id] = correct_answer
#     except FileNotFoundError:
#         print(f"Error: The file '{filename}' was not found.")
#         raise
#     return correct_answers

# def score_and_sort_responses(response_filename: str, answers_dict: dict, output_filename: str) -> bool:
#     """Reads student responses, calculates scores, sorts them, and writes to a new file."""
#     try:
#         with open(response_filename, mode='r', newline='', encoding='utf-8') as response_file:
#             reader = csv.reader(response_file)
#             original_header = next(reader)
#             question_headers = original_header[1:]
            
#             all_student_scores = []
#             for student_row in reader:
#                 if not student_row: continue
#                 student_id = student_row[0]
#                 new_score_row = [student_id]
#                 total_score = 0
#                 # Ensure student_row has enough columns
#                 for i, question_id in enumerate(question_headers):
#                     if i + 1 < len(student_row):
#                         student_answer = student_row[i + 1]
#                         if answers_dict.get(question_id) == student_answer:
#                             new_score_row.append(1)
#                             total_score += 1
#                         else:
#                             new_score_row.append(0)
#                     else:
#                         new_score_row.append(0) # Mark as incorrect if answer is missing
                
#                 new_score_row.append(total_score)
#                 all_student_scores.append(new_score_row)

#         all_student_scores.sort(key=lambda row: row[-1], reverse=True)
        
#         num_students = len(all_student_scores)
#         group_size = math.ceil(num_students * 0.27)
#         final_output_data = []
#         if num_students > 5 and (2 * group_size) < num_students:
#             num_columns = len(original_header) + 1
#             top_group = all_student_scores[:group_size]
#             middle_group = all_student_scores[group_size:-group_size]
#             bottom_group = all_student_scores[-group_size:]
            
#             top_separator = ['----'] * num_columns
#             top_separator[1] = '--- TOP 27% ---'
#             bottom_separator = ['----'] * num_columns
#             bottom_separator[1] = '--- BOTTOM 27% ---'
            
#             final_output_data.extend(top_group)
#             final_output_data.append(top_separator)
#             final_output_data.extend(middle_group)
#             final_output_data.append(bottom_separator)
#             final_output_data.extend(bottom_group)
#         else:
#             final_output_data = all_student_scores

#         with open(output_filename, mode='w', newline='', encoding='utf-8') as score_file:
#             writer = csv.writer(score_file)
#             writer.writerow(original_header + ['Total'])
#             writer.writerows(final_output_data)
#         return True
#     except (FileNotFoundError, IndexError) as e:
#         print(f"Error during scoring: {e}")
#         raise

# def perform_item_analysis(scores_filename: str, original_responses_filename: str, output_filename: str):
#     """Calculates all item analysis metrics with full level descriptions."""
#     try:
#         with open(original_responses_filename, mode='r', newline='', encoding='utf-8') as original_file:
#             original_reader = csv.reader(original_file)
#             next(original_reader) # Skip header
#             original_responses = list(original_reader)
#             all_options = sorted(list(set(answer for row in original_responses for answer in row[1:])))

#         with open(scores_filename, mode='r', newline='', encoding='utf-8') as scores_file:
#             reader = csv.reader(scores_file)
#             header = next(reader)
#             student_data = [row for row in reader if row and row[0] != '----']

#         if not student_data:
#             print("Error: No student data found.")
#             return

#         num_students = len(student_data)
#         group_size = math.ceil(num_students * 0.27)
#         top_group = student_data[:group_size]
#         bottom_group = student_data[-group_size:]
#         question_headers = header[1:-1]
#         all_total_scores = [int(row[-1]) for row in student_data]
#         s_t = calculate_std_dev(all_total_scores)
        
#         analysis_results = []
#         for i, question_id in enumerate(question_headers):
#             # --- Difficulty Index ---
#             total_correct = sum(int(row[i + 1]) for row in student_data)
#             difficulty_index = total_correct / num_students
#             if difficulty_index > 0.80: difficulty_level = "Easy"
#             elif difficulty_index >= 0.71: difficulty_level = "Moderately easy"
#             elif difficulty_index >= 0.51: difficulty_level = "Average"
#             elif difficulty_index >= 0.31: difficulty_level = "Moderately difficult"
#             else: difficulty_level = "Difficult"

#             # --- Discrimination Index ---
#             top_correct = sum(int(row[i + 1]) for row in top_group)
#             bottom_correct = sum(int(row[i + 1]) for row in bottom_group)
#             discrimination_index = abs((top_correct / group_size) - (bottom_correct / group_size)) if group_size > 0 else 0.0
#             if discrimination_index > 0.39: discrimination_level = "Excellent"
#             elif discrimination_index >= 0.30: discrimination_level = "Good"
#             elif discrimination_index >= 0.20: discrimination_level = "Regular"
#             else: discrimination_level = "Poor"

#             # --- Point-Biserial Correlation ---
#             scores_correct = [int(row[-1]) for row in student_data if int(row[i+1]) == 1]
#             scores_incorrect = [int(row[-1]) for row in student_data if int(row[i+1]) == 0]
#             m1 = sum(scores_correct) / len(scores_correct) if scores_correct else 0
#             m0 = sum(scores_incorrect) / len(scores_incorrect) if scores_incorrect else 0
#             p = len(scores_correct) / num_students if num_students > 0 else 0
#             q = 1 - p
#             point_biserial = abs(((m1 - m0) / s_t) * math.sqrt(p * q)) if s_t > 0 and p > 0 and q > 0 else 0.0
#             if point_biserial >= 0.40: point_biserial_level = "Very good"
#             elif point_biserial >= 0.30: point_biserial_level = "Good"
#             elif point_biserial >= 0.20: point_biserial_level = "Acceptable"
#             else: point_biserial_level = "Poor"

#             # --- Distractor Efficiency ---
#             option_counts = Counter(row[i + 1] for row in original_responses if i + 1 < len(row))
#             distractor_counter = sum(1 for opt in all_options if (option_counts.get(opt, 0) / num_students) * 100 > 5)
#             distractor_index = (distractor_counter - 1) / distractor_counter if distractor_counter > 1 else 0.0
#             if distractor_index >= 0.75: distractor_efficiency = "Excellent"
#             elif distractor_index >= 0.66: distractor_efficiency = "Moderate"
#             elif distractor_index >= 0.50: distractor_efficiency = "Poor"
#             else: distractor_efficiency = "Very poor"
            
#             result_row = [question_id, f"{difficulty_index:.2f}", f"{discrimination_index:.2f}", f"{point_biserial:.2f}"]
#             result_row.extend(option_counts.get(opt, 0) for opt in all_options)
#             result_row.extend([
#                 f"{distractor_index:.2f}",
#                 difficulty_level,
#                 discrimination_level,
#                 point_biserial_level,
#                 distractor_efficiency
#             ])
#             analysis_results.append(result_row)
            
#         new_header = ['Item_Identifier', 'Difficulty_Index', 'Discrimination_Index', 'Point_Biserial_Correlation']
#         new_header.extend(f'Count_Option_{opt}' for opt in all_options)
#         new_header.extend(['Distractor_Index', 'Difficulty_Level', 'Discrimination_Level', 'Point_Biserial_Level', 'Distractor_Efficiency'])
        
#         with open(output_filename, mode='w', newline='', encoding='utf-8') as analysis_file:
#             writer = csv.writer(analysis_file)
#             writer.writerow(new_header)
#             writer.writerows(analysis_results)
#     except (FileNotFoundError, ValueError, IndexError) as e:
#         print(f"Error during analysis: {e}")
#         raise

# def run_full_analysis_pipeline(answer_key_path: Path, responses_path: Path, scores_output_path: Path, analysis_output_path: Path):
#     """A synchronous wrapper that executes the entire analysis pipeline."""
#     correct_answers_map = load_correct_answers(str(answer_key_path))
#     if not correct_answers_map:
#         raise ValueError(f"Could not load or parse answer key: {answer_key_path}")

#     if score_and_sort_responses(str(responses_path), correct_answers_map, str(scores_output_path)):
#         perform_item_analysis(str(scores_output_path), str(responses_path), str(analysis_output_path))


# # --- FastAPI Endpoints ---

# @app.post("/upload-and-analyze/")
# async def create_upload_and_process_files(
#     answer_key: UploadFile = File(..., description="The answer key CSV file."),
#     student_responses: UploadFile = File(..., description="The student responses CSV file.")
# ):
#     """
#     Upload an answer key and student responses, save them to a new batch
#     directory, run the full analysis, and return the paths to the output files.
#     """
#     batch_path = get_next_batch_path()
#     try:
#         answer_key_path = batch_path / "answer_key.csv"
#         responses_path = batch_path / "student_responses.csv"
#         scores_output_path = batch_path / "student_scores.csv"
#         analysis_output_path = batch_path / "analysis.csv"

#         with open(answer_key_path, "wb") as buffer:
#             shutil.copyfileobj(answer_key.file, buffer)
#         with open(responses_path, "wb") as buffer:
#             shutil.copyfileobj(student_responses.file, buffer)

#         await run_in_threadpool(
#             run_full_analysis_pipeline,
#             answer_key_path=answer_key_path,
#             responses_path=responses_path,
#             scores_output_path=scores_output_path,
#             analysis_output_path=analysis_output_path
#         )

#         return {
#             "message": "Analysis completed successfully!",
#             "batch_directory": str(batch_path),
#             "output_files": {
#                 "scores_file": str(scores_output_path),
#                 "analysis_file": str(analysis_output_path)
#             }
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"An error occurred during analysis: {str(e)}")


# @app.get("/download/{batch_name}/{file_name}")
# async def download_file(batch_name: str, file_name: str):
#     """
#     Allows downloading of the generated analysis files.
#     """
#     # Construct the full path to the requested file
#     file_path = INPUT_DIR / batch_name / file_name

#     # Security check: Ensure the file exists before attempting to send it
#     if not file_path.is_file():
#         raise HTTPException(status_code=404, detail="File not found")
    
#     # Security check: Only allow downloading of expected output files
#     if file_name not in ["student_scores.csv", "analysis.csv"]:
#         raise HTTPException(status_code=403, detail="Access to this file is forbidden")

#     # Use FileResponse to stream the file to the client
#     return FileResponse(path=str(file_path), media_type='text/csv', filename=file_name)


# @app.get("/")
# async def root():
#     return {"message": "Welcome! Send a POST request to /upload-and-analyze/ to run an analysis."}


import csv
import math
import os
import shutil
from pathlib import Path
from collections import Counter
from typing import Dict, List

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.concurrency import run_in_threadpool
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uvicorn
import pandas as pd # Import pandas for Excel conversion

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Item Analysis API",
    description="Upload student responses and an answer key to perform automated item analysis.",
)

# --- CORS (Cross-Origin Resource Sharing) Configuration ---
origins = [
    "http://localhost",
    "http://localhost:3000", # Default React dev server port
    "http://localhost:5173", # Default Vite dev server port
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods (GET, POST, etc.)
    allow_headers=["*"], # Allows all headers
)


# --- Directory Setup for Storing Uploaded Files ---
INPUT_DIR = Path("input_file")
INPUT_DIR.mkdir(exist_ok=True)


# --- Helper Function to Manage Batch Directories ---
def get_next_batch_path() -> Path:
    """
    Determines the next batch directory path (e.g., input_file/batch_1, input_file/batch_2).
    """
    existing_batches = [d for d in INPUT_DIR.iterdir() if d.is_dir() and d.name.startswith("batch_")]

    if not existing_batches:
        next_batch_num = 1
    else:
        max_num = 0
        for batch_dir in existing_batches:
            try:
                num = int(batch_dir.name.split("_")[1])
                if num > max_num:
                    max_num = num
            except (IndexError, ValueError):
                continue
        next_batch_num = max_num + 1

    batch_path = INPUT_DIR / f"batch_{next_batch_num}"
    batch_path.mkdir(exist_ok=True)
    return batch_path


# --- Core Analysis Functions ---

def calculate_std_dev(data: list) -> float:
    """Calculates the population standard deviation for a list of numbers."""
    n = len(data)
    if n < 2:
        return 0.0
    mean = sum(data) / n
    variance = sum((x - mean) ** 2 for x in data) / n
    return math.sqrt(variance)

def calculate_variance(data: list) -> float:
    """Calculates the population variance for a list of numbers."""
    n = len(data)
    if n < 2:
        return 0.0
    mean = sum(data) / n
    variance = sum((x - mean) ** 2 for x in data) / n
    return variance

def load_correct_answers(filename: str) -> Dict[str, str]:
    """Reads the answer key CSV file and returns a dictionary of correct answers."""
    correct_answers = {}
    try:
        with open(filename, mode='r', newline='', encoding='utf-8') as answer_file:
            reader = csv.reader(answer_file)
            try:
                first_row = next(reader)
                if len(first_row) >= 2 and not (len(first_row[1]) > 1 or first_row[1].islower()):
                    correct_answers[first_row[0]] = first_row[1]
            except StopIteration:
                return {} # File is empty

            # Process the rest of the file
            for row in reader:
                if len(row) == 2:
                    question_id, correct_answer = row
                    correct_answers[question_id] = correct_answer
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
        raise
    return correct_answers

def score_and_sort_responses(response_filename: str, answers_dict: Dict[str, str], output_filename: str) -> bool:
    """Reads student responses, calculates scores, sorts them, and writes to a new file."""
    try:
        with open(response_filename, mode='r', newline='', encoding='utf-8') as response_file:
            reader = csv.reader(response_file)
            original_header = next(reader)
            question_headers = original_header[1:]

            all_student_scores = []
            for student_row in reader:
                if not student_row: continue
                student_id = student_row[0]
                new_score_row = [student_id]
                total_score = 0

                for i, question_id in enumerate(question_headers):
                    if i + 1 < len(student_row):
                        student_answer = student_row[i + 1]
                        if answers_dict.get(question_id) == student_answer:
                            new_score_row.append(1)
                            total_score += 1
                        else:
                            new_score_row.append(0)
                    else:
                        new_score_row.append(0) # Mark as incorrect if answer is missing

                new_score_row.append(total_score)
                all_student_scores.append(new_score_row)

        all_student_scores.sort(key=lambda row: row[-1], reverse=True)

        num_students = len(all_student_scores)
        group_size = math.ceil(num_students * 0.27)
        final_output_data = []
        if num_students > 5 and (2 * group_size) < num_students:
            num_columns = len(original_header) + 1
            top_group = all_student_scores[:group_size]
            middle_group = all_student_scores[group_size:-group_size]
            bottom_group = all_student_scores[-group_size:]

            top_separator = ['----'] * num_columns
            top_separator[1] = '--- TOP 27% ---'
            bottom_separator = ['----'] * num_columns
            bottom_separator[1] = '--- BOTTOM 27% ---'

            final_output_data.extend(top_group)
            final_output_data.append(top_separator)
            final_output_data.extend(middle_group)
            final_output_data.append(bottom_separator)
            final_output_data.extend(bottom_group)
        else:
            final_output_data = all_student_scores

        with open(output_filename, mode='w', newline='', encoding='utf-8') as score_file:
            writer = csv.writer(score_file)
            writer.writerow(original_header + ['Total'])
            writer.writerows(final_output_data)
        return True
    except (FileNotFoundError, IndexError) as e:
        print(f"Error during scoring: {e}")
        raise HTTPException(status_code=500, detail=f"Error during scoring: {e}")

def perform_item_analysis(scores_filename: str, original_responses_filename: str, output_filename: str):
    """Calculates all item analysis metrics with full level descriptions."""
    try:
        with open(original_responses_filename, mode='r', newline='', encoding='utf-8') as original_file:
            original_reader = csv.reader(original_file)
            next(original_reader) # Skip header
            original_responses = list(original_reader)

            all_options = set()
            for row in original_responses:
                for answer in row[1:]: # Iterate over student answers for each question
                    all_options.add(answer)
            sorted_options = sorted(list(all_options))


        with open(scores_filename, mode='r', newline='', encoding='utf-8') as scores_file:
            reader = csv.reader(scores_file)
            header = next(reader)
            student_data = [row for row in reader if row and row[0] != '----']

        if not student_data:
            print("Error: No student data found.")
            raise HTTPException(status_code=400, detail="No student data found for item analysis.")

        num_students = len(student_data)
        group_size = math.ceil(num_students * 0.27)
        top_group = student_data[:group_size]
        bottom_group = student_data[-group_size:]
        question_headers = header[1:-1]
        all_total_scores = [int(row[-1]) for row in student_data]
        s_t = calculate_std_dev(all_total_scores)

        analysis_results = []
        for i, question_id in enumerate(question_headers):
            # --- Difficulty Index ---
            total_correct = sum(int(row[i + 1]) for row in student_data)
            difficulty_index = total_correct / num_students
            if difficulty_index > 0.80: difficulty_level = "Easy"
            elif difficulty_index >= 0.71: difficulty_level = "Moderately easy"
            elif difficulty_index >= 0.51: difficulty_level = "Average"
            elif difficulty_index >= 0.31: difficulty_level = "Moderately difficult"
            else: difficulty_level = "Difficult"

            # --- Discrimination Index ---
            top_correct = sum(int(row[i + 1]) for row in top_group)
            bottom_correct = sum(int(row[i + 1]) for row in bottom_group)
            discrimination_index = abs((top_correct / group_size) - (bottom_correct / group_size)) if group_size > 0 else 0.0
            if discrimination_index > 0.39: discrimination_level = "Excellent"
            elif discrimination_index >= 0.30: discrimination_level = "Good"
            elif discrimination_index >= 0.20: discrimination_level = "Regular"
            else: discrimination_level = "Poor"

            # --- Point-Biserial Correlation ---
            scores_correct = [int(row[-1]) for row in student_data if int(row[i+1]) == 1]
            scores_incorrect = [int(row[-1]) for row in student_data if int(row[i+1]) == 0]
            m1 = sum(scores_correct) / len(scores_correct) if scores_correct else 0
            m0 = sum(scores_incorrect) / len(scores_incorrect) if scores_incorrect else 0
            p = len(scores_correct) / num_students if num_students > 0 else 0
            q = 1 - p
            point_biserial = abs(((m1 - m0) / s_t) * math.sqrt(p * q)) if s_t > 0 and p > 0 and q > 0 else 0.0
            if point_biserial >= 0.40: point_biserial_level = "Very good"
            elif point_biserial >= 0.30: point_biserial_level = "Good"
            elif point_biserial >= 0.20: point_biserial_level = "Acceptable"
            else: point_biserial_level = "Poor"

            # --- Distractor Efficiency ---
            # Ensure we are counting answers from the correct question column in original_responses
            option_counts = Counter(row[i + 1] for row in original_responses if i + 1 < len(row))
            distractor_counter = sum(1 for opt in sorted_options if (option_counts.get(opt, 0) / num_students) * 100 > 5)
            distractor_index = (distractor_counter - 1) / distractor_counter if distractor_counter > 1 else 0.0
            if distractor_index >= 0.75: distractor_efficiency = "Excellent"
            elif distractor_index >= 0.66: distractor_efficiency = "Moderate"
            elif distractor_index >= 0.50: distractor_efficiency = "Poor"
            else: distractor_efficiency = "Very poor"

            result_row = [question_id, f"{difficulty_index:.2f}", f"{discrimination_index:.2f}", f"{point_biserial:.2f}"]
            result_row.extend(option_counts.get(opt, 0) for opt in sorted_options)
            result_row.extend([
                f"{distractor_index:.2f}",
                difficulty_level,
                discrimination_level,
                point_biserial_level,
                distractor_efficiency
            ])
            analysis_results.append(result_row)

        new_header = ['Item_Identifier', 'Difficulty_Index', 'Discrimination_Index', 'Point_Biserial_Correlation']
        new_header.extend(f'Count_Option_{opt}' for opt in sorted_options)
        new_header.extend(['Distractor_Index', 'Difficulty_Level', 'Discrimination_Level', 'Point_Biserial_Level', 'Distractor_Efficiency'])

        with open(output_filename, mode='w', newline='', encoding='utf-8') as analysis_file:
            writer = csv.writer(analysis_file)
            writer.writerow(new_header)
            writer.writerows(analysis_results)
    except (FileNotFoundError, ValueError, IndexError) as e:
        print(f"Error during analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Error during item analysis: {e}")


def calculate_excluded_scores(scores_filename: str, output_filename: str) -> bool:
    """
    Calculates the total score for each student excluding one question at a time.
    For each student, it generates 'score_ex_qX' columns.
    """
    try:
        with open(scores_filename, mode='r', newline='', encoding='utf-8') as scores_file:
            reader = csv.reader(scores_file)
            header = next(reader)  # Read the header row

            student_id_col = header[0]
            question_headers = header[1:-1] # Question headers are all except first (ID) and last (Total)
            total_score_index = len(header) - 1 # Index of the 'Total' score column

            processed_data = []

            new_header = [student_id_col]
            for q_id in question_headers:
                new_header.append(f'Score_Ex_{q_id}')

            for row in reader:
                if not row or row[0] == '----': # Skip empty rows or separator rows
                    continue

                student_id = row[0]
                try:
                    total_score = int(row[total_score_index])
                except (ValueError, IndexError):
                    raise ValueError(f"Invalid total score or missing column in row: {row}")

                try:
                    question_scores = [int(score) for score in row[1:total_score_index]]
                except (ValueError, IndexError):
                    raise ValueError(f"Invalid question score or missing column in row: {row}")

                student_excluded_scores_row = [student_id]

                for i in range(len(question_scores)):
                    score_excluding_current_q = total_score - question_scores[i]
                    student_excluded_scores_row.append(score_excluding_current_q)

                processed_data.append(student_excluded_scores_row)

        with open(output_filename, mode='w', newline='', encoding='utf-8') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(new_header)
            writer.writerows(processed_data)

        return True

    except (FileNotFoundError, ValueError, IndexError) as e:
        print(f"Error during excluded score calculation: {e}")
        raise HTTPException(status_code=500, detail=f"Error during excluded score calculation: {e}")


def calculate_p_q_values(scores_filename: str, excluded_scores_filename: str, output_filename: str):
    """
    Calculates p (percent correct), q (percent wrong), p*q,
    variance of total score, variance of score excluding the current item,
    the KR-20 variant for each item, and the overall KR-20 for the test.
    """
    try:
        with open(scores_filename, mode='r', newline='', encoding='utf-8') as scores_file:
            reader = csv.reader(scores_file)
            header = next(reader)
            question_ids = header[1:-1]

            all_student_scores_data = []
            for row in reader:
                if row and row[0] != '----':
                    all_student_scores_data.append(row)

            if not all_student_scores_data:
                raise ValueError("No student data found in the scores file to calculate p and q values.")

            num_students = len(all_student_scores_data)
            num_questions = len(question_ids)

            all_total_scores = [int(row[-1]) for row in all_student_scores_data]
            total_test_variance = calculate_variance(all_total_scores)

            excluded_scores_per_student_per_item = {}
            with open(excluded_scores_filename, mode='r', newline='', encoding='utf-8') as excluded_file:
                ex_reader = csv.reader(excluded_file)
                ex_header = next(ex_reader)

                ex_score_col_map = {q_id: ex_header.index(f'Score_Ex_{q_id}') for q_id in question_ids}

                for row in ex_reader:
                    if row:
                        student_id = row[0]
                        excluded_scores_per_student_per_item[student_id] = [
                            float(row[ex_score_col_map[q_id]]) for q_id in question_ids
                        ]

        p_q_results = []
        all_p_q_products = []

        for i, question_id in enumerate(question_ids):
            correct_answers_for_question = [int(row[i + 1]) for row in all_student_scores_data]
            num_correct = sum(correct_answers_for_question)
            p = num_correct / num_students
            q = 1 - p
            p_times_q = p * q
            all_p_q_products.append(p_times_q)

        kr20_total = 0.0
        sum_of_all_pq = sum(all_p_q_products)
        if num_questions > 1 and total_test_variance > 0:
            kr20_total = (num_questions / (num_questions - 1)) * \
                         (1 - (sum_of_all_pq / total_test_variance))
        else:
            kr20_total = float('nan')

        for i, question_id in enumerate(question_ids):
            p = sum(int(row[i + 1]) for row in all_student_scores_data) / num_students
            q = 1 - p
            p_times_q = p * q

            sum_pq_excluding_current = sum_of_all_pq - all_p_q_products[i]

            current_item_excluded_total_scores = []
            for student_row in all_student_scores_data:
                student_id = student_row[0]
                if student_id in excluded_scores_per_student_per_item:
                    current_item_excluded_total_scores.append(excluded_scores_per_student_per_item[student_id][i])

            variance_excluded_item = calculate_variance(current_item_excluded_total_scores)

            kr20_variant_for_item = 0.0
            k_prime = num_questions - 1
            if k_prime > 1 and variance_excluded_item > 0:
                kr20_variant_for_item = (k_prime / (k_prime - 1)) * \
                                        (1 - (sum_pq_excluding_current / variance_excluded_item))
            else:
                kr20_variant_for_item = float('nan')

            p_q_results.append([
                question_id,
                f"{p:.4f}",
                f"{q:.4f}",
                f"{p_times_q:.4f}",
                f"{variance_excluded_item:.4f}",
                f"{kr20_variant_for_item:.4f}"
            ])

        with open(output_filename, mode='w', newline='', encoding='utf-8') as output_file:
            writer = csv.writer(output_file)
            writer.writerow([
                'Question_ID', 'p (Percent Correct)', 'q (Percent Wrong)', 'p*q',
                'Variance_Score_Ex_Item', 'KR20_Variant_For_Item'
            ])
            writer.writerows(p_q_results)

            writer.writerow([])
            writer.writerow(['Overall Test KR-20', f"{kr20_total:.4f}"])

    except (FileNotFoundError, ValueError, IndexError) as e:
        print(f"Error during P, Q, and Variance calculation: {e}")
        raise HTTPException(status_code=500, detail=f"Error during P, Q, and Variance calculation: {e}")


def run_full_analysis_pipeline(
    answer_key_path: Path,
    responses_path: Path,
    scores_output_path: Path,
    analysis_output_path: Path,
    p_q_output_path: Path,
    excluded_scores_path: Path,
    excel_output_path: Path
):
    """A synchronous wrapper that executes the entire analysis pipeline."""
    try:
        correct_answers_map = load_correct_answers(str(answer_key_path))
        if not correct_answers_map:
            raise ValueError(f"Could not load or parse answer key: {answer_key_path}")

        if score_and_sort_responses(str(responses_path), correct_answers_map, str(scores_output_path)):
            calculate_excluded_scores(str(scores_output_path), str(excluded_scores_path))
            perform_item_analysis(str(scores_output_path), str(responses_path), str(analysis_output_path))
            calculate_p_q_values(str(scores_output_path), str(excluded_scores_path), str(p_q_output_path))

            # Combine all CSVs into a single Excel file
            with pd.ExcelWriter(excel_output_path, engine='openpyxl') as writer:
                scores_df = pd.read_csv(scores_output_path)
                scores_df.to_excel(writer, sheet_name='Student Scores', index=False)

                analysis_df = pd.read_csv(analysis_output_path)
                analysis_df.to_excel(writer, sheet_name='Item Analysis', index=False)

                p_q_df = pd.read_csv(p_q_output_path)
                p_q_df.to_excel(writer, sheet_name='P-Q Values & KR20', index=False)

                excluded_df = pd.read_csv(excluded_scores_path)
                excluded_df.to_excel(writer, sheet_name='Excluded Scores (KR)', index=False)

    except Exception as e:
        # Clean up created files if an error occurs during processing
        for path in [scores_output_path, analysis_output_path, p_q_output_path, excluded_scores_path, excel_output_path]:
            if path.exists():
                os.remove(path)
        raise e


# --- FastAPI Endpoints ---

@app.post("/upload-and-analyze/")
async def create_upload_and_process_files(
    answer_key: UploadFile = File(..., description="The answer key CSV file."),
    student_responses: UploadFile = File(..., description="The student responses CSV file.")
):
    """
    Upload an answer key and student responses, save them to a new batch
    directory, run the full analysis, and return the path to the combined Excel file.
    """
    batch_path = get_next_batch_path()

    answer_key_path = batch_path / "answer_key.csv"
    responses_path = batch_path / "student_responses.csv"
    scores_output_path = batch_path / "student_scores.csv"
    analysis_output_path = batch_path / "analysis.csv"
    p_q_output_path = batch_path / "p_q_item_kr20_values.csv"
    excluded_scores_path = batch_path / "excluded_scores_kr.csv"
    final_excel_output_path = batch_path / "item_analysis_report.xlsx" # The Excel file

    try:
        with open(answer_key_path, "wb") as buffer:
            shutil.copyfileobj(answer_key.file, buffer)
        with open(responses_path, "wb") as buffer:
            shutil.copyfileobj(student_responses.file, buffer)

        await run_in_threadpool(
            run_full_analysis_pipeline,
            answer_key_path=answer_key_path,
            responses_path=responses_path,
            scores_output_path=scores_output_path,
            analysis_output_path=analysis_output_path,
            p_q_output_path=p_q_output_path,
            excluded_scores_path=excluded_scores_path,
            excel_output_path=final_excel_output_path
        )

        return {
            "message": "Analysis completed successfully!",
            "batch_directory": str(batch_path),
            "output_file": str(final_excel_output_path) # Return the path to the Excel file
        }
    except Exception as e:
        # Clean up the batch directory if an error occurred during processing
        if batch_path.exists():
            shutil.rmtree(batch_path)
        raise HTTPException(status_code=500, detail=f"An error occurred during analysis: {str(e)}")


@app.get("/download/{batch_name}/{file_name}")
async def download_file(batch_name: str, file_name: str):
    """
    Allows downloading of the final combined Excel report ('item_analysis_report.xlsx') ONLY.
    """
    file_path = INPUT_DIR / batch_name / file_name

    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    # Security check: ONLY allow downloading of 'item_analysis_report.xlsx'
    if file_name != "item_analysis_report.xlsx":
        raise HTTPException(status_code=403, detail="Access to this file is forbidden. Only 'item_analysis_report.xlsx' can be downloaded.")

    # Determine media type based on file extension
    if file_name.endswith(".xlsx"):
        media_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    else:
        # Fallback for other types, though only .xlsx is expected here
        media_type = 'application/octet-stream'

    return FileResponse(path=str(file_path), media_type=media_type, filename=file_name)


@app.get("/")
async def root():
    return {"message": "Welcome! Send a POST request to /upload-and-analyze/ to run an analysis."}