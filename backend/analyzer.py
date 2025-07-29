import csv
import math
from collections import Counter
import pandas as pd
import os # Import os for file operations (cleanup)

def calculate_std_dev(data):
    """Calculates the population standard deviation for a list of numbers."""
    n = len(data)
    if n < 2:
        return 0.0
    mean = sum(data) / n
    variance = sum((x - mean) ** 2 for x in data) / n
    return math.sqrt(variance)

def calculate_variance(data):
    """Calculates the population variance for a list of numbers."""
    n = len(data)
    if n < 2:
        return 0.0
    mean = sum(data) / n
    variance = sum((x - mean) ** 2 for x in data) / n
    return variance

def load_correct_answers(filename):
    """
    Reads the answer key CSV file and returns a dictionary of correct answers.
    This version is independent of the header names.
    """
    correct_answers = {}
    try:
        with open(filename, mode='r', newline='') as answer_file:
            reader = csv.reader(answer_file)
            # Read the first row to determine if it's a header or data
            try:
                first_row = next(reader)
                # Simple heuristic: if the second column's value is longer than one character,
                # or not a typical option, assume it's a header. This can be adjusted.
                if len(first_row) > 1 and (len(first_row[1]) > 1 or first_row[1].islower() or not first_row[0].isdigit()):
                    # This was a header, so we do nothing and move on.
                    pass
                else:
                    # This was data, so we process it.
                    if len(first_row) == 2:
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
        return None
    return correct_answers

def score_and_sort_responses(response_filename, answers_dict, output_filename):
    """
    Reads student responses, calculates scores, sorts them, and writes to a new file.
    This version is independent of the header names.
    """
    try:
        with open(response_filename, mode='r', newline='') as response_file:
            reader = csv.reader(response_file)
            # Read the original header to use in the output file
            original_header = next(reader)
            # The first column is treated as the student identifier column
            # The rest are treated as question columns
            question_headers = original_header[1:]
            
            all_student_scores = []

            for student_row in reader:
                if not student_row: continue
                # The first element of the row is the student identifier
                student_id = student_row[0]
                new_score_row = [student_id]
                total_score = 0

                # Loop through the answer columns (from the second column onwards)
                for i in range(len(question_headers)):
                    question_id = question_headers[i]
                    # The student's answer is at index i + 1
                    student_answer = student_row[i + 1]
                    
                    if answers_dict.get(question_id) == student_answer:
                        new_score_row.append(1)
                        total_score += 1
                    else:
                        new_score_row.append(0)
                
                new_score_row.append(total_score)
                all_student_scores.append(new_score_row)

        all_student_scores.sort(key=lambda row: row[-1], reverse=True)
        
        # The rest of the logic for segregation remains the same
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

        with open(output_filename, mode='w', newline='') as score_file:
            writer = csv.writer(score_file)
            # Write the original header plus a 'Total' column
            writer.writerow(original_header + ['Total'])
            writer.writerows(final_output_data)
        
        print(f"Scoring and sorting complete. Results saved to '{output_filename}'.")
        return True

    except FileNotFoundError:
        print(f"Error: The file '{response_filename}' was not found.")
        return False
    except IndexError:
        print(f"Error: A row in '{response_filename}' does not have enough columns. Please check the file format.")
        return False


def perform_item_analysis(scores_filename, original_responses_filename, output_filename):
    """
    Calculates all item analysis metrics, dynamically detecting answer options
    and independent of column names.
    """
    try:
        # --- Read original responses to find all possible answer options ---
        with open(original_responses_filename, mode='r', newline='') as original_file:
            original_reader = csv.reader(original_file)
            next(original_reader) # Skip header
            original_responses = list(original_reader)
            
            all_options = set()
            for row in original_responses:
                for answer in row[1:]:
                    all_options.add(answer)
            sorted_options = sorted(list(all_options))

        # --- Read the scored data for analysis ---
        with open(scores_filename, mode='r', newline='') as scores_file:
            reader = csv.reader(scores_file)
            header = next(reader)
            
            all_data = list(reader)
            student_data = [row for row in all_data if row and row[0] != '----']

            if not student_data:
                print("Error: No student data found. Cannot perform analysis.")
                return

            num_students = len(student_data)
            group_size = math.ceil(num_students * 0.27)
            
            top_group = student_data[:group_size]
            bottom_group = student_data[-group_size:]

            # The question headers are all columns except the first (ID) and last (Total)
            question_headers = header[1:-1]
            num_questions = len(question_headers)
            
            all_total_scores = [int(row[-1]) for row in student_data]
            s_t = calculate_std_dev(all_total_scores)

            analysis_results = []

            for i in range(num_questions):
                question_id = question_headers[i]
                
                # --- Calculations for each metric ---
                total_correct = sum(int(row[i + 1]) for row in student_data)
                difficulty_index = total_correct / num_students
                
                if difficulty_index > 0.80: difficulty_level = "Easy"
                elif difficulty_index >= 0.71: difficulty_level = "Moderately easy"
                elif difficulty_index >= 0.51: difficulty_level = "Average"
                elif difficulty_index >= 0.31: difficulty_level = "Moderately difficult"
                else: difficulty_level = "Difficult"

                top_group_correct = sum(int(row[i + 1]) for row in top_group)
                bottom_group_correct = sum(int(row[i + 1]) for row in bottom_group)

                if group_size == 0: discrimination_index = 0.0
                else:
                    top_group_percent = top_group_correct / group_size
                    bottom_group_percent = bottom_group_correct / group_size
                    discrimination_index = abs(top_group_percent - bottom_group_percent)
                
                if discrimination_index > 0.39: discrimination_level = "Excellent"
                elif discrimination_index >= 0.30: discrimination_level = "Good"
                elif discrimination_index >= 0.20: discrimination_level = "Regular"
                else: discrimination_level = "Poor"

                scores_of_correct = [int(row[-1]) for row in student_data if int(row[i+1]) == 1]
                scores_of_incorrect = [int(row[-1]) for row in student_data if int(row[i+1]) == 0]
                m1 = sum(scores_of_correct) / len(scores_of_correct) if scores_of_correct else 0
                m0 = sum(scores_of_incorrect) / len(scores_of_incorrect) if scores_of_incorrect else 0
                p = len(scores_of_correct) / num_students
                q = 1 - p

                if s_t > 0 and p > 0 and q > 0: point_biserial = abs(((m1 - m0) / s_t) * math.sqrt(p * q))
                else: point_biserial = 0.0
                
                if point_biserial >= 0.40: point_biserial_level = "Very good"
                elif point_biserial >= 0.30: point_biserial_level = "Good"
                elif point_biserial >= 0.20: point_biserial_level = "Acceptable"
                else: point_biserial_level = "Poor"

                question_column_index = i + 1
                all_answers_for_question = [row[question_column_index] for row in original_responses]
                option_counts = Counter(all_answers_for_question)
                
                distractor_counter = 0
                for option in sorted_options:
                    percentage = (option_counts.get(option, 0) / num_students) * 100
                    if percentage > 5:
                        distractor_counter += 1
                
                if distractor_counter > 1: distractor_index = (distractor_counter - 1) / distractor_counter
                else: distractor_index = 0.0
                
                if distractor_index >= 0.75: distractor_efficiency = "Excellent"
                elif distractor_index >= 0.66: distractor_efficiency = "Moderate"
                elif distractor_index >= 0.50: distractor_efficiency = "Poor"
                else: distractor_efficiency = "Very poor"
                
                result_row = [
                    question_id, 
                    f"{difficulty_index:.2f}",
                    f"{discrimination_index:.2f}",
                    f"{point_biserial:.2f}"
                ]
                for option in sorted_options:
                    result_row.append(option_counts.get(option, 0))
                
                result_row.extend([
                    f"{distractor_index:.2f}",
                    difficulty_level,
                    discrimination_level,
                    point_biserial_level,
                    distractor_efficiency
                ])
                analysis_results.append(result_row)

        with open(output_filename, mode='w', newline='') as analysis_file:
            writer = csv.writer(analysis_file)
            
            new_header = [
                'Item_Identifier', 'Difficulty_Index', 'Discrimination_Index', 'Point_Biserial_Correlation'
            ]
            for option in sorted_options:
                new_header.append(f'Count_Option_{option}')
            new_header.extend([
                'Distractor_Index', 'Difficulty_Level', 'Discrimination_Level',
                'Point_Biserial_Level', 'Distractor_Efficiency'
            ])
            
            writer.writerow(new_header)
            writer.writerows(analysis_results)
        
        print(f"Item analysis complete. Results saved to '{output_filename}'.")

    except FileNotFoundError as e:
        print(f"Error: A required file was not found: {e.filename}")
    except (ValueError, IndexError) as e:
        print(f"An error occurred during analysis: {e}")
        print("Please ensure the data files are formatted correctly.")


def calculate_p_q_values(scores_filename, excluded_scores_filename, output_filename='p_q_item_kr20_values.csv'):
    """
    Calculates p (percent correct), q (percent wrong), p*q,
    variance of total score, variance of score excluding the current item,
    the KR-20 variant for each item, and the overall KR-20 for the test.
    """
    try:
        # Read scores file
        with open(scores_filename, mode='r', newline='') as scores_file:
            reader = csv.reader(scores_file)
            header = next(reader)  # Read the header
            question_ids = header[1:-1] # Question headers are all except first (ID) and last (Total)
            
            all_student_scores_data = []
            for row in reader:
                if row and row[0] != '----':  # Skip separator rows
                    all_student_scores_data.append(row)

            if not all_student_scores_data:
                print("No student data found in the scores file to calculate p and q values.")
                return

            num_students = len(all_student_scores_data)
            num_questions = len(question_ids)
            
            # Extract all total scores for the overall test variance
            all_total_scores = [int(row[-1]) for row in all_student_scores_data]
            total_test_variance = calculate_variance(all_total_scores)

            # Read excluded scores data from the excluded_scores_filename
            excluded_scores_per_student_per_item = {}
            with open(excluded_scores_filename, mode='r', newline='') as excluded_file:
                ex_reader = csv.reader(excluded_file)
                ex_header = next(ex_reader) # Header for excluded scores
                
                # Create a mapping from question_id to its column index in the excluded scores file
                ex_score_col_map = {q_id: ex_header.index(f'Score_Ex_{q_id}') for q_id in question_ids}

                for row in ex_reader:
                    if row:
                        student_id = row[0]
                        excluded_scores_per_student_per_item[student_id] = [
                            float(row[ex_score_col_map[q_id]]) for q_id in question_ids
                        ]

        p_q_results = []
        all_p_q_products = [] # To store p*q for all items for KR-20 formula

        for i, question_id in enumerate(question_ids):
            # Calculate p, q, p*q for the current question
            correct_answers_for_question = [int(row[i + 1]) for row in all_student_scores_data]
            num_correct = sum(correct_answers_for_question)
            p = num_correct / num_students
            q = 1 - p
            p_times_q = p * q
            all_p_q_products.append(p_times_q)

        # Calculate the overall KR-20 (KR20_Total)
        kr20_total = 0.0
        sum_of_all_pq = sum(all_p_q_products)
        if num_questions > 1 and total_test_variance > 0: # KR-20 requires at least 2 questions
            kr20_total = (num_questions / (num_questions - 1)) * \
                         (1 - (sum_of_all_pq / total_test_variance))
        else:
            kr20_total = float('nan') # Not meaningful for 1 or 0 questions

        # Now, calculate item-level KR-20 variant for each item
        for i, question_id in enumerate(question_ids):
            p = sum(int(row[i + 1]) for row in all_student_scores_data) / num_students # Recalculate p for display
            q = 1 - p
            p_times_q = p * q

            # Sum of p*q excluding the current item's p*q
            sum_pq_excluding_current = sum_of_all_pq - all_p_q_products[i]

            # Collect scores excluding the current item for all students
            current_item_excluded_total_scores = []
            for student_row in all_student_scores_data:
                student_id = student_row[0]
                if student_id in excluded_scores_per_student_per_item:
                    current_item_excluded_total_scores.append(excluded_scores_per_student_per_item[student_id][i])
                # else: Removed warning to prevent excessive output for valid cases

            # Calculate variance of scores with the current item excluded
            variance_excluded_item = calculate_variance(current_item_excluded_total_scores)

            kr20_variant_for_item = 0.0
            if num_questions > 2 and variance_excluded_item > 0: # For (k-2) in denominator
                kr20_variant_for_item = ((num_questions - 1) / (num_questions - 2)) * \
                              (1 - (sum_pq_excluding_current / variance_excluded_item))
            elif num_questions <= 2:
                kr20_variant_for_item = float('nan') # Not meaningful for 2 or fewer questions
            
            p_q_results.append([
                question_id,
                f"{p:.4f}",
                f"{q:.4f}",
                f"{p_times_q:.4f}", # This is the p*q for the current item
                f"{variance_excluded_item:.4f}", # Variance of score EXCLUDING current item
                f"{kr20_variant_for_item:.4f}"
            ])

        with open(output_filename, mode='w', newline='') as output_file:
            writer = csv.writer(output_file)
            writer.writerow([
                'Question_ID', 'p (Percent Correct)', 'q (Percent Wrong)', 'p*q',
                'Variance_Score_Ex_Item', 'KR20_Variant_For_Item'
            ])
            writer.writerows(p_q_results)
            
            # Add the overall KR20_Total as a summary row
            writer.writerow([]) # Blank row for separation
            writer.writerow(['Overall Test KR-20', f"{kr20_total:.4f}"])
        
        print(f"P, Q, P*Q values, excluded item variances, Item KR-20 variant, and Overall Test KR-20 calculated and saved to '{output_filename}'.")

    except FileNotFoundError:
        print(f"Error: One or more required files were not found for P, Q, and Variance calculation.")
        print(f"Please ensure '{scores_filename}' and '{excluded_scores_filename}' exist.")
    except Exception as e:
        print(f"An error occurred during P, Q, and Variance calculation: {e}")


def calculate_excluded_scores(scores_filename, output_filename='excluded_scores_kr.csv'):
    """
    Calculates the total score for each student excluding one question at a time.
    For each student, it generates 'score_ex_qX' columns.
    """
    try:
        with open(scores_filename, mode='r', newline='') as scores_file:
            reader = csv.reader(scores_file)
            header = next(reader)  # Read the header row
            
            # Find the indices for student ID, question scores, and total score
            student_id_col = header[0]
            # Question headers are from index 1 up to the second-to-last column (excluding 'Total')
            question_headers = header[1:-1]
            total_score_index = len(header) - 1 # Index of the 'Total' score column

            processed_data = []
            
            # Prepare the new header for the output file
            new_header = [student_id_col]
            for q_id in question_headers:
                new_header.append(f'Score_Ex_{q_id}') # e.g., 'Score_Ex_Q1', 'Score_Ex_Q2'
            
            for row in reader:
                if not row or row[0] == '----': # Skip empty rows or separator rows
                    continue
                
                student_id = row[0]
                total_score = int(row[total_score_index])
                
                # Convert question scores to integers for calculation
                question_scores = [int(score) for score in row[1:total_score_index]]
                
                student_excluded_scores_row = [student_id]
                
                # Calculate score excluding each question
                for i in range(len(question_scores)):
                    # Subtract the score of the current question from the total score
                    score_excluding_current_q = total_score - question_scores[i]
                    student_excluded_scores_row.append(score_excluding_current_q)
                
                processed_data.append(student_excluded_scores_row)

        with open(output_filename, mode='w', newline='') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(new_header)
            writer.writerows(processed_data)
        
        print(f"Excluded scores calculated and saved to '{output_filename}'.")
        return True

    except FileNotFoundError:
        print(f"Error: The scores file '{scores_filename}' was not found for excluded score calculation.")
        return False
    except (ValueError, IndexError) as e:
        print(f"An error occurred during excluded score calculation: {e}")
        print("Please ensure the scored data file is correctly formatted with numerical scores.")
        return False


# --- Main execution block ---
if __name__ == "__main__":
    # --- Get file paths from user input ---
    print("Welcome to the Item Analysis Tool.")
    answer_key_file = input("➡️ Enter the path for the answer key CSV file: ")
    student_responses_file = input("➡️ Enter the path for the student responses CSV file: ")

    # Define the output filenames (these will be temporary CSVs, then combined)
    scores_output_csv = 'temp_student_scores.csv' # Temporary CSV
    analysis_output_csv = 'temp_analysis.csv'     # Temporary CSV
    p_q_output_csv = 'p_q_item_kr20_values.csv'   # Final CSV for P, Q, and Item KR-20 + Overall KR-20
    excluded_scores_csv = 'temp_excluded_scores_kr.csv' # Temporary CSV for excluded scores
    
    final_excel_output_file = 'item_analysis_report.xlsx' # Final Excel output

    print("\n" + "="*40 + "\n")

    # --- Step 1: Loading Correct Answers ---
    print("--- Step 1: Loading Correct Answers ---")
    correct_answers_map = load_correct_answers(answer_key_file)

    if correct_answers_map:
        print(f"✅ Answers loaded successfully from '{answer_key_file}'.")
        print("\n" + "="*40 + "\n")
        
        # --- Step 2: Scoring, Sorting, and Segregating Student Responses ---
        print("--- Step 2: Scoring and Sorting Student Responses ---")
        if score_and_sort_responses(student_responses_file, correct_answers_map, scores_output_csv):
            print("\n" + "="*40 + "\n")

            # --- Step 3: Calculating Excluded Scores (Needed before P,Q calc now) ---
            print("--- Step 3: Calculating Excluded Scores ---")
            if calculate_excluded_scores(scores_output_csv, excluded_scores_csv):
                print("\n" + "="*40 + "\n")
                
                # --- Step 4: Performing Item Analysis ---
                # This still needs the original responses to get all options, and the scored data
                print("--- Step 4: Performing Item Analysis ---")
                perform_item_analysis(scores_output_csv, student_responses_file, analysis_output_csv)
                print("\n" + "="*40 + "\n")

                # --- Step 5: Calculating P, Q, P*Q values, excluded item variances, and the Item KR-20 Variant ---
                print("--- Step 5: Calculating P, Q, P*Q Values, Variances, Item KR-20 Variant, and Overall Test KR-20 ---")
                calculate_p_q_values(scores_output_csv, excluded_scores_csv, p_q_output_csv)
                print("\n" + "="*40 + "\n")
                
                # --- Step 6: Combining all CSVs into a single Excel file with sheets ---
                print("--- Step 6: Consolidating Results into Excel ---")
                try:
                    with pd.ExcelWriter(final_excel_output_file, engine='openpyxl') as writer:
                        # Read each temporary CSV and write to a different sheet
                        scores_df = pd.read_csv(scores_output_csv)
                        scores_df.to_excel(writer, sheet_name='Student Scores', index=False)
                        print(f"Added 'Student Scores' to '{final_excel_output_file}'.")

                        analysis_df = pd.read_csv(analysis_output_csv)
                        analysis_df.to_excel(writer, sheet_name='Item Analysis', index=False)
                        print(f"Added 'Item Analysis' to '{final_excel_output_file}'.")

                        p_q_df = pd.read_csv(p_q_output_csv)
                        p_q_df.to_excel(writer, sheet_name='P-Q Values & Item KR20', index=False) # Updated sheet name
                        print(f"Added 'P-Q Values & Item KR20' to '{final_excel_output_file}'.")

                        excluded_df = pd.read_csv(excluded_scores_csv)
                        excluded_df.to_excel(writer, sheet_name='Excluded Scores (KR)', index=False)
                        print(f"Added 'Excluded Scores (KR)' to '{final_excel_output_file}'.")
                    
                    print(f"\n✅ All results successfully combined into '{final_excel_output_file}'.")

                    # Optional: Clean up temporary CSV files
                    os.remove(scores_output_csv)
                    os.remove(analysis_output_csv)
                    os.remove(p_q_output_csv)
                    os.remove(excluded_scores_csv)
                    print("Cleaned up temporary CSV files.")

                except Exception as e:
                    print(f"An error occurred while creating the Excel file: {e}")
                
                print("\n" + "="*40 + "\n")
                print("All analysis steps completed.")
            else:
                print("Skipping further analysis due to error in calculating excluded scores.")
        else:
            print("Skipping further analysis due to error in scoring and sorting responses.")
    else:
        print("Skipping further analysis due to error in loading correct answers.")