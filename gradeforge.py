import json
import csv
import os

from student import Student, HighSchoolStudent, CollegeStudent, GRADE_POINTS, VALID_LETTER_GRADES
from subject import Subject
from grade import Grade

DATA_FILE = "gradeforge_data.json"

class GradeForge:
    """
    Main class for the GradeForge CLI application.
    Manages students, subjects, and program data.
    """
    def __init__(self):
        self.students: dict[str, Student] = {} # student_id -> Student object
        self.available_subjects: dict[str, Subject] = {} # subject_code -> Subject object
        self.load_data()

    def add_student(self):
        """Prompts user for student details and adds a new student to the system."""
        print("\n--- Add New Student ---")
        name = input("Enter student name: ").strip()
        student_id = input("Enter student ID: ").strip()
        student_type_choice = input("Enter student type (1: High School, 2: College, Enter for Generic Student): ").strip().lower()

        if not name or not student_id:
            print("Error: Student name and ID cannot be empty.")
            return

        if student_id in self.students:
            print(f"Error: Student with ID {student_id} already exists.")
            return

        try:
            if student_type_choice == '1':
                student = HighSchoolStudent(name, student_id)
            elif student_type_choice == '2':
                major = input("Enter college student's major (e.g., Computer Science): ").strip()
                student = CollegeStudent(name, student_id, major if major else "Undeclared")
            else:
                student = Student(name, student_id) # Generic student type
            
            self.students[student_id] = student
            print(f"Student {name} ({student_id}) added successfully as {student.__class__.__name__}.")
        except ValueError as e:
            print(f"Error adding student: {e}")


    def _get_student(self) -> Student | None:
        """Helper to get a student by ID."""
        if not self.students:
            print("No students in the system yet.")
            return None
        student_id = input("Enter student ID: ").strip()
        student = self.students.get(student_id)
        if not student:
            print(f"Student with ID {student_id} not found.")
            return None
        return student

    def _get_subject_from_available(self, prompt_for_new: bool = True) -> Subject | None:
        """Helper to get an existing subject or create a new one to be available."""
        if self.available_subjects:
            print("Available subjects (templates):")
            for code, subj in self.available_subjects.items():
                print(f"  {code}: {subj.name} ({subj.credit_hours} credits)")
        else:
            print("No subjects globally available yet.")

        subject_code = input("Enter subject code: ").strip().upper()
        subject = self.available_subjects.get(subject_code)

        if not subject and prompt_for_new:
            create_new = input(f"Subject with code {subject_code} not found. Create new global template? (y/n): ").lower()
            if create_new == 'y':
                subject_name = input(f"Enter name for subject {subject_code}: ").strip()
                # Credit hours are not set for templates; they are set during assignment to CollegeStudent
                if subject_name:
                    try:
                        subject = Subject(subject_name, subject_code) # Will use default credit_hours=0
                        self.available_subjects[subject_code] = subject
                        print(f"Subject template {subject_name} ({subject_code}) created.")
                    except ValueError as e:
                        print(f"Error creating subject: {e}")
                else:
                    print("Subject name cannot be empty.")
                    return None
            else:
                return None
        elif not subject:
            print(f"Subject with code {subject_code} not found in global templates.")
            return None
        return subject
        
    def assign_subject_to_student(self):
        """Assigns an existing or new subject to a student."""
        print("\n--- Assign Subject to Student ---")
        student = self._get_student()
        if not student:
            return

        print(f"Assigning subject to {student.name} ({student.student_id}).")
        # Get a subject template (which now includes credit hours)
        subject_template = self._get_subject_from_available(prompt_for_new=True)

        if subject_template:
            try:
                # Student gets their own instance of the subject, copying details from the template
                # Credit hours will be the default (e.g., 0) from the template initially
                student_specific_subject = Subject(name=subject_template.name, 
                                                 code=subject_template.code, 
                                                 credit_hours=subject_template.credit_hours) # Keeps template's default CH

                if isinstance(student, CollegeStudent):
                    while True:
                        try:
                            ch_str = input(f"Enter credit hours for {student_specific_subject.name} for {student.name} (e.g., 3): ").strip()
                            credit_hours_for_student = int(ch_str)
                            if credit_hours_for_student < 0:
                                print("Credit hours cannot be negative. Please try again.")
                                continue
                            student_specific_subject.credit_hours = credit_hours_for_student
                            break
                        except ValueError:
                            print("Invalid input for credit hours. Please enter a whole number.")
                
                # For HighSchoolStudent or generic Student, credit_hours will remain the default (e.g., 0) 
                # and won't be actively used in their calculations.

                student.enroll_subject(student_specific_subject)
                print(f"Subject {student_specific_subject.name} ({student_specific_subject.credit_hours} credits used if College) assigned to {student.name}.")
            except ValueError as e:
                print(f"Error assigning subject: {e}")


    def input_grades_for_subject(self):
        """Inputs grades for a specific subject for a given student based on their type."""
        print("\n--- Input Grades for Subject ---")
        student = self._get_student()
        if not student:
            return

        if not student.enrolled_subjects:
            print(f"{student.name} is not enrolled in any subjects.")
            return

        print(f"Enrolled subjects for {student.name}:")
        for code, subj in student.enrolled_subjects.items():
            print(f"  {code}: {subj.name} ({subj.credit_hours} credits)")
        
        subject_code = input("Enter subject code to add grades for: ").strip().upper()
        
        if subject_code not in student.enrolled_subjects:
            print(f"Error: {student.name} is not enrolled in subject {subject_code}.")
            return

        current_subject = student.enrolled_subjects[subject_code] # Renamed for clarity
        print(f"Inputting grades for {current_subject.name} ({current_subject.code}) for student {student.name} ({student.__class__.__name__}).")
        
        while True:
            grade_desc = input("Enter grade description (e.g., Midterm, Assignment 1) or 'done' to finish: ").strip()
            if grade_desc.lower() == 'done':
                break
            if not grade_desc:
                print("Grade description cannot be empty.")
                continue
            
            grade_obj = None
            try:
                if isinstance(student, CollegeStudent):
                    while True:
                        letter_grade_input = input(f"Enter letter grade for '{grade_desc}' ({', '.join(VALID_LETTER_GRADES)}): ").strip().upper()
                        if letter_grade_input in VALID_LETTER_GRADES:
                            point = GRADE_POINTS[letter_grade_input]
                            grade_obj = Grade(description=grade_desc, score=point, letter_grade=letter_grade_input)
                            break
                        else:
                            print(f"Invalid letter grade. Please choose from: {', '.join(VALID_LETTER_GRADES)}.")
                elif isinstance(student, HighSchoolStudent) or isinstance(student, Student):
                    # Handles HighSchoolStudent and generic Student with numeric grades
                    while True:
                        try:
                            score_str = input(f"Enter numeric score for '{grade_desc}' (0-100): ").strip()
                            score_val = float(score_str)
                            if not (0 <= score_val <= 100):
                                print("Score must be between 0 and 100. Please try again.")
                                continue
                            grade_obj = Grade(description=grade_desc, score=score_val)
                            break
                        except ValueError:
                            print("Invalid input. Score must be a number.")
                else:
                    print("Error: Unknown student type. Cannot input grades.")
                    # This case should ideally not be reached if student creation is controlled
                    # Adding a break here to prevent infinite loop if it somehow occurs
                    break 

                if grade_obj:
                    student.add_grade_to_subject(subject_code, grade_obj)
                    print(f"Grade '{str(grade_obj)}' added to {current_subject.name}.")

            except ValueError as e: # Catches errors from Grade or Student methods if they raise ValueError
                print(f"Error processing grade: {e}. Please try again.")
            except Exception as e: # Catch any other unexpected error during grade input attempt
                print(f"An unexpected error occurred while inputting grade: {e}. Please try again.")


    def calculate_performance(self):
        """Calculates and displays subject-wise and overall performance for a student."""
        print("\n--- Calculate Student Performance ---")
        student = self._get_student()
        if not student:
            return

        print(f"\nPerformance Summary for {student.name} ({student.student_id} - {student.__class__.__name__}):")
        if not student.enrolled_subjects:
            print("No subjects enrolled.")
            return

        try:
            if isinstance(student, CollegeStudent):
                print(f"  Overall GPA: {student.get_gpa():.2f}")
                print(f"  Academic Status: {student.get_pass_fail_status()}")
                if student.check_for_f_grades():
                    print("  Alert: Student has one or more 'F' grades.")
                print("  For detailed subject grades, please use the 'Generate Student Report' option.")
            elif isinstance(student, HighSchoolStudent) or isinstance(student, Student):
                # For HighSchoolStudent and generic Student, show detailed subject averages here
                for subject_code, subject_obj in student.enrolled_subjects.items():
                    avg = subject_obj.get_average_grade()
                    print(f"  Subject: {subject_obj.name} ({subject_code}) - Average Mark: {avg:.2f}")
                    if not subject_obj.grades:
                        print("    No grades recorded for this subject.")
                    else:
                        for grade_item in subject_obj.grades:
                            print(f"      - {str(grade_item)}") # Uses Grade.__str__
                overall_avg = student.get_overall_average()
                pass_fail_status = student.get_pass_fail_status() # Uses 50% threshold by default
                print(f"\n  Overall Average Mark: {overall_avg:.2f}")
                print(f"  Status: {pass_fail_status}")
            else:
                 print("Error: Unknown student type for performance calculation.")
        except Exception as e:
            print(f"Error calculating performance: {e}")


    def generate_student_report(self):
        """Generates and displays a detailed report for a student."""
        print("\n--- Generate Student Report ---")
        student = self._get_student()
        if not student:
            return
        try:
            print(student.generate_report()) # Polymorphic call to the correct report method
        except Exception as e:
            print(f"Error generating report: {e}")

    def export_to_csv(self):
        """Exports all student data to a CSV file."""
        print("\n--- Export Data to CSV ---")
        if not self.students:
            print("No student data to export.")
            return

        filename = input("Enter CSV filename (e.g., gradeforge_export.csv): ").strip()
        if not filename:
            filename = "gradeforge_export.csv"
        if not filename.lower().endswith(".csv"):
            filename += ".csv"

        try:
            with open(filename, 'w', newline='') as csvfile:
                fieldnames = [
                    'student_id', 'student_name', 'student_type', 'major',
                    'subject_code', 'subject_name', 'subject_credit_hours',
                    'grade_description', 'grade_score_or_point', 'letter_grade',
                    'subject_average_or_gpa_points', 'overall_average_mark_or_gpa', 'status'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for student_id, student in self.students.items():
                    student_type_name = student.__class__.__name__
                    major_val = student.major if isinstance(student, CollegeStudent) else None
                    overall_perf = student.get_overall_average() # GPA for College, Avg Mark for HS
                    status_val = student.get_pass_fail_status()
                    
                    if not student.enrolled_subjects:
                        writer.writerow({
                            'student_id': student.student_id,
                            'student_name': student.name,
                            'student_type': student_type_name,
                            'major': major_val,
                            'overall_average_mark_or_gpa': f"{overall_perf:.2f}",
                            'status': status_val
                        })
                    else:
                        for subj_code, enrolled_subject_obj in student.enrolled_subjects.items(): # Renamed for clarity
                            subj_avg_points_or_mark = enrolled_subject_obj.get_average_grade()
                            if not enrolled_subject_obj.grades:
                                writer.writerow({
                                    'student_id': student.student_id,
                                    'student_name': student.name,
                                    'student_type': student_type_name,
                                    'major': major_val,
                                    'subject_code': enrolled_subject_obj.code,
                                    'subject_name': enrolled_subject_obj.name,
                                    'subject_credit_hours': enrolled_subject_obj.credit_hours,
                                    'subject_average_or_gpa_points': f"{subj_avg_points_or_mark:.2f}",
                                    'overall_average_mark_or_gpa': f"{overall_perf:.2f}",
                                    'status': status_val
                                })
                            else:
                                for grade_item in enrolled_subject_obj.grades:
                                    writer.writerow({
                                        'student_id': student.student_id,
                                        'student_name': student.name,
                                        'student_type': student_type_name,
                                        'major': major_val,
                                        'subject_code': enrolled_subject_obj.code,
                                        'subject_name': enrolled_subject_obj.name,
                                        'subject_credit_hours': enrolled_subject_obj.credit_hours,
                                        'grade_description': grade_item.description,
                                        'grade_score_or_point': f"{grade_item.score:.2f}", # Numeric mark for HS, Grade Point for College
                                        'letter_grade': grade_item.letter_grade, # Null for HS
                                        'subject_average_or_gpa_points': f"{subj_avg_points_or_mark:.2f}",
                                        'overall_average_mark_or_gpa': f"{overall_perf:.2f}",
                                        'status': status_val
                                    })
            print(f"Data exported successfully to {filename}")
        except IOError as e:
            print(f"Error exporting to CSV: {e}")
        except Exception as e:
            print(f"An unexpected error occurred during CSV export: {e}")


    def save_data(self):
        """Saves the current session data to a JSON file."""
        data_to_save = {
            "students": {},
            "available_subjects": {}
        }
        try:
            for student_id, student_obj in self.students.items():
                subjects_data = {}
                for subj_code, subj_instance in student_obj.enrolled_subjects.items(): # Renamed for clarity
                    grades_data = []
                    for g in subj_instance.grades:
                        grades_data.append({
                            "description": g.description, 
                            "score": g.score, # Numeric mark for HS, Grade Point for College
                            "letter_grade": g.letter_grade # Present for CollegeStudent grades
                        })
                    subjects_data[subj_code] = {
                        "name": subj_instance.name,
                        "code": subj_instance.code,
                        "credit_hours": subj_instance.credit_hours, # Save credit hours
                        "grades": grades_data
                    }
                student_data = {
                    "name": student_obj.name,
                    "student_id": student_obj.student_id,
                    "type": student_obj.__class__.__name__,
                    "enrolled_subjects": subjects_data
                }
                if isinstance(student_obj, CollegeStudent):
                    student_data["major"] = student_obj.major
                data_to_save["students"][student_id] = student_data

            for subj_code, subj_template in self.available_subjects.items(): # Renamed for clarity
                data_to_save["available_subjects"][subj_code] = {
                    "name": subj_template.name,
                    "code": subj_template.code,
                    "credit_hours": subj_template.credit_hours # Save credit hours for available subjects too
                }
            
            with open(DATA_FILE, 'w') as f:
                json.dump(data_to_save, f, indent=4)
            print(f"Data saved successfully to {DATA_FILE}")
        except IOError as e:
            print(f"Error saving data: {e}")
        except Exception as e:
            print(f"An unexpected error occurred during data save: {e}")


    def load_data(self):
        """Loads data from the JSON file if it exists."""
        if not os.path.exists(DATA_FILE):
            # print(f"No data file ({DATA_FILE}) found. Starting with an empty system.") # Less verbose startup
            return

        try:
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)

            self.available_subjects = {}
            loaded_available_subjects = data.get("available_subjects", {})
            for subj_code, subj_data in loaded_available_subjects.items():
                try:
                    # Provide default for credit_hours for backward compatibility if old data file exists
                    self.available_subjects[subj_code] = Subject(name=subj_data["name"], 
                                                                 code=subj_data["code"], 
                                                                 credit_hours=subj_data.get("credit_hours", 3))
                except (KeyError, ValueError) as e:
                    print(f"Warning: Could not load available subject {subj_code}. Data: {subj_data}. Error: {e}")

            self.students = {}
            loaded_students = data.get("students", {})
            for student_id, student_data in loaded_students.items():
                try:
                    student_name = student_data["name"]
                    student_type = student_data.get("type", "Student")
                    
                    current_student_obj: Student # Type hint for clarity
                    if student_type == "HighSchoolStudent":
                        current_student_obj = HighSchoolStudent(student_name, student_id)
                    elif student_type == "CollegeStudent":
                        major = student_data.get("major", "Undeclared")
                        current_student_obj = CollegeStudent(student_name, student_id, major)
                    else:
                        current_student_obj = Student(student_name, student_id)

                    loaded_enrolled_subjects = student_data.get("enrolled_subjects", {})
                    for subj_code, subj_data_enrolled in loaded_enrolled_subjects.items():
                        try:
                            enrolled_subject_instance = Subject( # Renamed for clarity
                                name=subj_data_enrolled["name"],
                                code=subj_data_enrolled["code"],
                                credit_hours=subj_data_enrolled.get("credit_hours", 3)
                            )
                            loaded_grades = subj_data_enrolled.get("grades", [])
                            for grade_data in loaded_grades:
                                try:
                                    grade_item = Grade( # Renamed for clarity
                                        description=grade_data["description"],
                                        score=float(grade_data["score"]), 
                                        letter_grade=grade_data.get("letter_grade")
                                    )
                                    enrolled_subject_instance.add_grade(grade_item)
                                except (KeyError, ValueError) as e:
                                    print(f"Warning: Could not load grade for {student_name} in {subj_data_enrolled.get('name', 'N/A')}. Data: {grade_data}. Error: {e}")
                            current_student_obj.enroll_subject(enrolled_subject_instance)
                        except (KeyError, ValueError) as e:
                             print(f"Warning: Could not load enrolled subject {subj_code} for student {student_name}. Data: {subj_data_enrolled}. Error: {e}")        
                    self.students[student_id] = current_student_obj
                except (KeyError, ValueError) as e:
                    print(f"Warning: Could not load student {student_id}. Data: {student_data}. Error: {e}")
            
            if loaded_available_subjects or loaded_students:
                print(f"Data loaded successfully from {DATA_FILE}")

        except FileNotFoundError:
            # print(f"Data file {DATA_FILE} not found. Starting with an empty system.") # Expected first run
            pass 
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from {DATA_FILE}: {e}. Starting with an empty system.")
        except Exception as e:
            print(f"An unexpected error occurred during data load: {e}. Starting with an empty system.")

    def list_all_students(self):
        """Lists all students in the system."""
        print("\n--- All Students ---")
        if not self.students:
            print("No students in the system.")
            return
        for student_id, student in self.students.items():
            # Use student.__str__() for a concise summary, which is overridden by CollegeStudent for GPA
            print(f"- {str(student)}") 

    def list_available_subjects(self):
        """Lists all globally available subjects (templates)."""
        print("\n--- Available Subjects (Templates) ---")
        if not self.available_subjects:
            print("No subjects defined in the system yet.")
            return
        for code, subject in self.available_subjects.items():
            # Use subject.__str__() for a concise summary including credit hours
            print(f"- {str(subject)}")

    def delete_student(self):
        """Deletes a student from the system after confirmation."""
        print("\n--- Delete Student ---")
        student = self._get_student() # Uses the helper to find student by ID
        if not student:
            return # _get_student already prints not found message

        confirm = input(f"Are you sure you want to delete student {student.name} (ID: {student.student_id})? This action cannot be undone. (y/n): ").strip().lower()
        if confirm == 'y':
            try:
                del self.students[student.student_id]
                print(f"Student {student.name} (ID: {student.student_id}) has been deleted.")
                # Consider if related data in available_subjects needs cleanup; currently not necessary
                # as subjects are templates.
            except KeyError:
                print(f"Error: Student {student.name} (ID: {student.student_id}) was already removed or an issue occurred.")
            except Exception as e:
                print(f"An unexpected error occurred while deleting student: {e}")
        else:
            print("Student deletion cancelled.")

    def run(self):
        """Runs the main CLI loop for GradeForge."""
        print("Welcome to GradeForge - Student Grade Management System!")
        while True:
            print("\n" + "="*40)
            print("Main Menu:")
            print("1. Add New Student")
            print("2. Assign Subject to Student")
            print("3. Input Grades for Subject")
            print("4. View Student Performance Summary") # Renamed for clarity
            print("5. Generate Full Student Report")   # Renamed for clarity
            print("6. List All Students")
            print("7. List Available Subjects (Templates)")
            print("8. Export All Data to CSV")
            print("9. Save Data")
            print("10. Delete Student") # New option
            print("0. Exit")
            print("="*40)

            choice = input("Enter your choice: ").strip()

            try:
                if choice == '1':
                    self.add_student()
                elif choice == '2':
                    self.assign_subject_to_student()
                elif choice == '3':
                    self.input_grades_for_subject()
                elif choice == '4':
                    self.calculate_performance()
                elif choice == '5':
                    self.generate_student_report()
                elif choice == '6':
                    self.list_all_students()
                elif choice == '7':
                    self.list_available_subjects()
                elif choice == '8':
                    self.export_to_csv()
                elif choice == '9':
                    self.save_data()
                elif choice == '10': # New choice handling
                    self.delete_student()
                elif choice == '0':
                    print("Saving data before exiting...")
                    self.save_data()
                    print("Exiting GradeForge. Goodbye!")
                    break
                else:
                    print("Invalid choice. Please try again.")
            except Exception as e:
                print(f"An unexpected error occurred in the main loop: {e}")
                # import traceback # For debugging uncomment this line
                # traceback.print_exc() # And this one

if __name__ == "__main__":
    app = GradeForge()
    app.run() 