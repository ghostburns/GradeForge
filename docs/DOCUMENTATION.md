# GradeForge Documentation
Version 1.0

## Table of Contents
- [GradeForge Documentation](#gradeforge-documentation)
  - [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
    - [Purpose](#purpose)
    - [Target Users](#target-users)
  - [System Architecture](#system-architecture)
    - [Overview](#overview)
    - [Core Modules (as Python files)](#core-modules-as-python-files)
  - [Object-Oriented Design](#object-oriented-design)
    - [Design Principles](#design-principles)
    - [Class Hierarchy](#class-hierarchy)
    - [Key Design Patterns Used](#key-design-patterns-used)
  - [Core Components](#core-components)
    - [Student Class (`student.py`)](#student-class-studentpy)
    - [HighSchoolStudent Class (`student.py`)](#highschoolstudent-class-studentpy)
    - [CollegeStudent Class (`student.py`)](#collegestudent-class-studentpy)
    - [Subject Class (`subject.py`)](#subject-class-subjectpy)
    - [Grade Class (`grade.py`)](#grade-class-gradepy)
  - [Data Management](#data-management)
    - [Data Storage](#data-storage)
    - [Data Structure (in `gradeforge_data.json`)](#data-structure-in-gradeforge_datajson)
    - [Data Operations (within `GradeForge` class)](#data-operations-within-gradeforge-class)
  - [User Interface (CLI)](#user-interface-cli)
  - [Features and Functionality](#features-and-functionality)
  - [Technical Specifications](#technical-specifications)
    - [System Requirements](#system-requirements)
    - [Error Handling \& Validation](#error-handling--validation)
    - [Logging](#logging)
  - [References](#references)
  - [Appendix](#appendix)
    - [Key Data Files and Constants](#key-data-files-and-constants)
    - [Example Workflow (CLI Interaction)](#example-workflow-cli-interaction)

## Introduction
GradeForge is a comprehensive academic management system designed to streamline the process of managing student grades, subjects, and academic records. This documentation provides a detailed overview of the system's architecture, components, and functionality, based on the actual Python codebase.

### Purpose
GradeForge serves as a centralized platform for:
- Managing student academic records for different student types (Generic, High School, College).
- Tracking subject enrollments and grades (numeric scores for High School, letter grades/points for College).
- Generating performance reports and transcripts.
- Persisting data locally using JSON.

### Target Users
- Educational administrators or individuals needing a simple system to manage student academic data.

## System Architecture

### Overview
GradeForge is built using Python. It features distinct classes for students, subjects, and grades. A main `GradeForge` class in `gradeforge.py` orchestrates user interactions via a command-line interface and manages data persistence.

### Core Modules (as Python files)
1.  **`student.py`:** Defines the base `Student` class and its specialized subclasses `HighSchoolStudent` and `CollegeStudent`.
2.  **`subject.py`:** Defines the `Subject` class, representing courses students can enroll in.
3.  **`grade.py`:** Defines the `Grade` class, representing individual grade entries.
4.  **`gradeforge.py`:** Contains the main `GradeForge` application class, handling CLI interactions, data loading/saving, and coordinating operations between students, subjects, and grades.

## Object-Oriented Design

### Design Principles

1.  **Single Responsibility Principle (SRP)**
    *   **Definition:** A class should have one primary responsibility.
    *   **GradeForge Implementation:**
        *   `Student` class: Manages student-specific data (ID, name) and basic enrollment.
        *   `Subject` class: Manages subject details (code, name, credit hours) and associated grades for a specific student enrollment.
        *   `Grade` class: Represents a single grade entry (description, score/point, optional letter grade).
        *   `GradeForge` class: Handles UI, data persistence, user-driven operations, and acts as an orchestrator.

2.  **Open/Closed Principle (OCP)**
    *   **Definition:** Software entities should be open for extension but closed for modification.
    *   **GradeForge Implementation:** The use of `Student` subclasses (`HighSchoolStudent`, `CollegeStudent`) demonstrates this. New student types with different grading or reporting logic can be added by creating new subclasses of `Student` without altering the base `Student` class or existing subclasses significantly. Methods like `get_overall_average()`, `get_pass_fail_status()`, and `generate_report()` are overridden in subclasses to provide specialized behavior.

3.  **Liskov Substitution Principle (LSP)**
    *   **Definition:** Subtypes must be substitutable for their base types.
    *   **GradeForge Implementation:** Instances of `HighSchoolStudent` and `CollegeStudent` can be (and are) stored in the `self.students` dictionary of the `GradeForge` class (which expects `Student` objects). Methods like `generate_report()` are called polymorphically on these objects.

4.  **Interface Segregation Principle (ISP)**
    *   **GradeForge Implementation:** While the system doesn't heavily use formal abstract base classes for interface segregation in the strictest sense, the classes have focused roles. For example, `Student` objects expose methods for enrollment and grade management, which `GradeForge` uses. Different student types then handle their specific internal logic for calculations and reporting.

5.  **Dependency Inversion Principle (DIP)**
    *   **GradeForge Implementation:** The `GradeForge` class directly instantiates and manages `Student`, `Subject`, and `Grade` objects. It handles data persistence internally rather than relying on injected repository abstractions. This is a simpler approach suitable for the application's current scale.

### Class Hierarchy
```
Student (from student.py)
├── HighSchoolStudent (from student.py)
└── CollegeStudent (from student.py)

Subject (from subject.py)
Grade (from grade.py)

GradeForge (from gradeforge.py - Orchestrator/Application Class)
```

### Key Design Patterns Used
1.  **Inheritance:** Central to the `Student` hierarchy, allowing `HighSchoolStudent` and `CollegeStudent` to share common functionality from `Student` while providing specialized implementations for grading, GPA calculation, and reporting.
2.  **Encapsulation:** Each class bundles its data (attributes) and the methods that operate on that data. For instance, `Student.enrolled_subjects` is managed internally, and subjects are added via `enroll_subject()`. `Grade` objects store score and description, with methods to represent themselves.
3.  **Polymorphism:** Demonstrated by methods like `generate_report()`, `get_overall_average()`, and `get_pass_fail_status()` in the `Student` hierarchy. Calling these methods on a `Student` object will execute the version specific to its actual type (`Student`, `HighSchoolStudent`, or `CollegeStudent`).

## Core Components

Detailed descriptions of the primary classes based on the source code.

### Student Class (`student.py`)
**Responsibility:** Base class representing a student, handling common attributes and operations.
**Key Attributes:**
*   `name (str)`: The name of the student.
*   `student_id (str)`: The unique ID of the student.
*   `enrolled_subjects (dict[str, Subject])`: Dictionary mapping subject codes to `Subject` objects the student is enrolled in.

**Constructor:**
```python
class Student:
    def __init__(self, name: str, student_id: str):
        if not isinstance(name, str) or not name:
            raise ValueError("Student name must be a non-empty string.")
        if not isinstance(student_id, str) or not student_id:
            raise ValueError("Student ID must be a non-empty string.")
        self.name = name
        self.student_id = student_id
        self.enrolled_subjects: dict[str, Subject] = {}
```

**Key Methods:**
*   `enroll_subject(self, subject: Subject)`: Enrolls the student in the given `Subject` object, adding it to `enrolled_subjects` keyed by `subject.code`. Raises `ValueError` if already enrolled or invalid subject.
*   `add_grade_to_subject(self, subject_code: str, grade: Grade)`: Adds a `Grade` object to the specified enrolled subject by calling `subject.add_grade(grade)`.
*   `get_subject_average(self, subject_code: str) -> float | None`: Retrieves an enrolled subject and calls its `get_average_grade()` method.
*   `get_overall_average(self) -> float`: Calculates the simple average of average grades from all enrolled subjects that have grades. Returns 0.0 if no subjects or no grades.
*   `get_pass_fail_status(self, threshold: float = 50.0) -> str`: Returns "Pass" or "Fail" based on the `get_overall_average()` and the provided threshold.
*   `generate_report(self) -> str`: Generates a basic text report including student details, enrolled subjects with their average grades, and overall performance.
*   `__str__(self)`: Returns a string like "Student Name: {self.name}, ID: {self.student_id}, Overall Avg: {self.get_overall_average():.2f}".
*   `__repr__(self)`: Returns `Student(name='{self.name}', student_id='{self.student_id}', subjects_count={len(self.enrolled_subjects)})`.

### HighSchoolStudent Class (`student.py`)
**Inherits from:** `Student`
**Responsibility:** Represents a high school student. Primarily uses numeric grades (0-100).
**Key Attributes:** Inherits all from `Student`. No additional attributes in its constructor.

**Constructor:**
```python
class HighSchoolStudent(Student):
    def __init__(self, name: str, student_id: str):
        super().__init__(name, student_id)
```
**Key Methods:** This class mostly utilizes the inherited methods from `Student`. The behavior of these methods (like `get_overall_average` and `generate_report`) is appropriate for numeric scoring as handled by the base `Student`, `Subject`, and `Grade` classes when `Grade.score` is a numeric mark.

### CollegeStudent Class (`student.py`)
**Inherits from:** `Student`
**Responsibility:** Represents a college student, using letter grades convertible to grade points for GPA calculation.
**Key Attributes:**
*   Inherits attributes from `Student`.
*   `major (str)`: The student's major, defaulting to "Undeclared".

**Constants (defined in `student.py`):**
*   `GRADE_POINTS (dict)`: Maps letter grades to grade points (e.g., `{"A+": 4.0, "A": 4.0, ... "F": 0.0}`).
*   `VALID_LETTER_GRADES (list)`: Derived from `GRADE_POINTS.keys()`.

**Constructor:**
```python
class CollegeStudent(Student):
    def __init__(self, name: str, student_id: str, major: str = "Undeclared"):
        super().__init__(name, student_id)
        self.major = major
```

**Key Methods (Overrides and Additions):**
*   `get_gpa(self) -> float`: Calculates the GPA. It iterates through enrolled subjects, gets the average grade points for each subject (via `subject.get_average_grade()`, where `grade.score` is a grade point), multiplies by `subject.credit_hours`, sums these up, and divides by total credit hours attempted.
*   `check_for_f_grades(self) -> bool`: Iterates through all grades of all enrolled subjects and returns `True` if any `grade.letter_grade` is "F".
*   `get_overall_average(self) -> float`: Overrides the base method to specifically return the result of `self.get_gpa()`.
*   `get_pass_fail_status(self, gpa_threshold_good_standing: float = 2.0) -> str`: Overrides base method. Determines academic standing ("Good Standing", "Academic Probation", "Academic Warning", "Failing") based on GPA and presence of 'F' grades.
*   `generate_report(self) -> str`: Overrides base method to produce a detailed report including major, GPA, academic status, and listing subjects with credit hours, grades (letter and points), and subject average points.
*   `__str__(self)`: Returns a string like "College Student: {self.name}, ID: {self.student_id}, Major: {self.major}, GPA: {self.get_gpa():.2f}".
*   `__repr__(self)`: Returns `CollegeStudent(name='{self.name}', student_id='{self.student_id}', major='{self.major}', gpa={self.get_gpa():.2f})`.

### Subject Class (`subject.py`)
**Responsibility:** Represents an academic subject or course. Each `Student` object holds its own instances of `Subject` for courses they are enrolled in.
**Key Attributes:**
*   `name (str)`: The name of the subject.
*   `code (str)`: The unique code for the subject.
*   `credit_hours (int)`: The number of credit hours for the subject (default 0). Crucial for `CollegeStudent` GPA.
*   `grades (list[Grade])`: A list of `Grade` objects recorded for this specific subject instance (i.e., for one student).

**Constructor:**
```python
class Subject:
    def __init__(self, name: str, code: str, credit_hours: int = 0):
        if not isinstance(name, str) or not name:
            raise ValueError("Subject name must be a non-empty string.")
        # ... other validations for code and credit_hours ...
        self.name = name
        self.code = code
        self.credit_hours = credit_hours
        self.grades: list[Grade] = []
```

**Key Methods:**
*   `add_grade(self, grade: Grade)`: Appends a `Grade` object to its `grades` list. Raises `ValueError` if a grade with the same description already exists.
*   `get_average_grade(self) -> float`: Calculates the average of the `score` attribute of all `Grade` objects in its `grades` list. If no grades, returns 0.0. (Note: for `CollegeStudent`, `grade.score` is a grade point; for `HighSchoolStudent`, it's a numeric mark).
*   `__str__(self)`: Returns "{self.name} ({self.code}, {self.credit_hours} credits) - Avg Score/Point: {self.get_average_grade():.2f}".
*   `__repr__(self)`: Returns `Subject(name='{self.name}', code='{self.code}', credit_hours={self.credit_hours}, grades_count={len(self.grades)})`.

### Grade Class (`grade.py`)
**Responsibility:** Represents a single grade entry for a component of a subject.
**Key Attributes:**
*   `description (str)`: Description of the graded item (e.g., "Midterm Exam", "Assignment 1").
*   `score (float)`: The numeric value of the grade. For `HighSchoolStudent`, this is the mark (0-100). For `CollegeStudent`, this is the **grade point** (e.g., 4.0 for an "A") corresponding to the `letter_grade`.
*   `letter_grade (str | None)`: The letter grade (e.g., "A+", "B-"), primarily used by `CollegeStudent`. Defaults to `None`.

**Constructor:**
```python
class Grade:
    def __init__(self, description: str, score: float, letter_grade: str | None = None):
        if not isinstance(description, str) or not description:
            raise ValueError("Description must be a non-empty string.")
        if not isinstance(score, (int, float)):
            raise ValueError("Score/Grade Point must be a number.")
        self.description = description
        self.score = float(score)
        self.letter_grade = letter_grade
```

**Key Methods:**
*   `__str__(self)`: Returns a string representation, e.g., "Midterm Exam: A+ (4.00 points)" if `letter_grade` is present, otherwise "Assignment 1: 85.00".
*   `__repr__(self)`: Returns a detailed string `Grade(description='{self.description}', score={self.score}, letter_grade='{self.letter_grade}')`.

## Data Management
Data persistence is managed by the `GradeForge` class methods (`save_data` and `load_data`) in `gradeforge.py`.

### Data Storage
-   **Primary Data File:** `gradeforge_data.json` (from `DATA_FILE = "gradeforge_data.json"`).
-   **Mechanism:** The `GradeForge` class serializes its `self.students` and `self.available_subjects` dictionaries into JSON format when saving, and deserializes them on loading.

### Data Structure (in `gradeforge_data.json`)
The `GradeForge.save_data()` method produces the following JSON structure:
```json
{
    "students": {
        "STUDENT_ID_1": {
            "name": "Student Name 1",
            "student_id": "STUDENT_ID_1",
            "type": "CollegeStudent", // or HighSchoolStudent, Student
            "major": "Computer Science", // Only for CollegeStudent
            "enrolled_subjects": {
                "SUBJ_CODE_A": {
                    "name": "Subject A Name",
                    "code": "SUBJ_CODE_A",
                    "credit_hours": 3,
                    "grades": [
                        {
                            "description": "Midterm",
                            "score": 3.7, // Grade point for College, numeric for HS
                            "letter_grade": "A-" // Null for HS
                        }
                        // ... more grades for this subject for this student
                    ]
                }
                // ... more subjects for this student
            }
        }
        // ... more students
    },
    "available_subjects": { // These are subject templates
        "SUBJ_CODE_X": {
            "name": "Template Subject X Name",
            "code": "SUBJ_CODE_X",
            "credit_hours": 0 // Or a default, as set when template created
        }
        // ... more available subject templates
    }
}
```

### Data Operations (within `GradeForge` class)

1.  **`load_data(self)`:**
    *   Checks if `DATA_FILE` exists. If not, starts with an empty system.
    *   Opens and reads the JSON file.
    *   Populates `self.available_subjects`: Iterates through the "available_subjects" data, creating `Subject` template objects.
    *   Populates `self.students`: Iterates through the "students" data.
        *   Determines student type ("HighSchoolStudent", "CollegeStudent", or "Student") and instantiates the correct class.
        *   For each student, iterates through their "enrolled_subjects" data.
            *   Creates a `Subject` instance for each enrolled subject (this is a student-specific instance, not from `available_subjects` directly after loading, but constructed with the saved details).
            *   For each subject, iterates through its "grades" data, creating `Grade` objects and adding them to the student's subject instance using `enrolled_subject_instance.add_grade(grade_item)`.
            *   Enrolls the student in this reconstructed subject instance using `current_student_obj.enroll_subject(enrolled_subject_instance)`.
    *   Includes `try-except` blocks for `FileNotFoundError`, `json.JSONDecodeError`, and `KeyError`/`ValueError` during object reconstruction, printing warnings for data that cannot be loaded.

2.  **`save_data(self)`:**
    *   Creates a `data_to_save` dictionary with top-level keys "students" and "available_subjects".
    *   **Students:** Iterates `self.students.items()`. For each `student_obj`:
        *   Creates a dictionary for the student including `name`, `student_id`, `type` (`student_obj.__class__.__name__`), and `major` (if `CollegeStudent`).
        *   Creates an `enrolled_subjects` dictionary for this student. For each `subj_instance` in `student_obj.enrolled_subjects.items()`:
            *   Serializes the subject's `name`, `code`, `credit_hours`.
            *   Serializes its `grades` list, where each grade is a dictionary with `description`, `score`, and `letter_grade`.
        *   Adds this student's data to `data_to_save["students"]` keyed by `student_id`.
    *   **Available Subjects:** Iterates `self.available_subjects.items()`. For each `subj_template`:
        *   Serializes its `name`, `code`, and `credit_hours`.
        *   Adds this template's data to `data_to_save["available_subjects"]` keyed by `subj_code`.
    *   Writes `data_to_save` to `DATA_FILE` using `json.dump()` with `indent=4`.
    *   Includes `IOError` and general `Exception` handling.

## User Interface (CLI)
The command-line interface is managed by the `run(self)` method within the `GradeForge` class (`gradeforge.py`). It presents a text-based menu to the user.

**Main Menu Options (from `GradeForge.run()`):**
```
========================================
Main Menu:
1. Add New Student
2. Assign Subject to Student
3. Input Grades for Subject
4. View Student Performance Summary
5. Generate Full Student Report
6. List All Students
7. List Available Subjects (Templates)
8. Export All Data to CSV
9. Save Data
10. Delete Student
0. Exit
========================================
Enter your choice:
```

**Interaction Flow:**
The `run()` method continuously displays this menu and waits for user input.
-   Based on the numeric `choice`, it calls a corresponding method in the `GradeForge` instance (e.g., `self.add_student()` for choice '1').
-   These methods then guide the user through further input prompts to gather necessary data (e.g., student name, subject codes, scores).
-   Feedback and results are printed to the console.
-   Choosing '0' (Exit) triggers `self.save_data()` before terminating the program. Option '9' allows explicit saving.

## Features and Functionality
Implemented via methods in the `GradeForge` class.

1.  **Student Management:**
    *   **Add New Student (`add_student`)**:
        *   Prompts for name, ID, and student type (1: High School, 2: College, Enter for Generic).
        *   Validates that name/ID are not empty and ID doesn't already exist.
        *   Creates `HighSchoolStudent`, `CollegeStudent` (prompts for major), or base `Student` object.
        *   Stores the new student in `self.students`.
    *   **List All Students (`list_all_students`)**: Iterates `self.students` and prints the `str()` representation of each student.
    *   **Delete Student (`delete_student`)**: Prompts for student ID. If found, asks for confirmation (y/n), then removes student from `self.students`.

2.  **Subject Management & Enrollment:**
    *   **Helper `_get_subject_from_available(prompt_for_new=True)`**:
        *   Lists available subject templates from `self.available_subjects`.
        *   Prompts for a subject code. If not found and `prompt_for_new` is true, asks to create a new global template (name, code; `credit_hours` defaults to 0 for templates).
        *   Returns the selected or newly created `Subject` template object.
    *   **Assign Subject to Student (`assign_subject_to_student`)**:
        *   Gets a student using `_get_student()`.
        *   Gets a subject template using `_get_subject_from_available()`.
        *   Creates a *new* `Subject` instance for the student, copying details (`name`, `code`, `credit_hours`) from the template.
        *   If the student is a `CollegeStudent`, prompts for the specific `credit_hours` for this enrollment, updating the new subject instance.
        *   Calls `student.enroll_subject()` with this student-specific `Subject` instance.
    *   **List Available Subjects (`list_available_subjects`)**: Iterates `self.available_subjects` and prints the `str()` representation of each template.

3.  **Grade Input (`input_grades_for_subject`)**:
    *   Gets a student using `_get_student()`.
    *   Lists student's enrolled subjects and prompts for a subject code.
    *   Loops, prompting for grade `description`.
    *   If `CollegeStudent`: Prompts for letter grade (from `VALID_LETTER_GRADES`), gets corresponding point from `GRADE_POINTS`, creates `Grade(description, point, letter_grade)`.
    *   If `HighSchoolStudent` or generic `Student`: Prompts for numeric score (0-100), creates `Grade(description, score_val)`.
    *   Calls `student.add_grade_to_subject(subject_code, grade_obj)`.

4.  **Performance Calculation & Reporting:**
    *   **Calculate Performance (`calculate_performance`)**:
        *   Gets a student.
        *   If `CollegeStudent`: Prints overall GPA, academic status (from `student.get_pass_fail_status()`), and F grade alert.
        *   If `HighSchoolStudent` or generic `Student`: Prints each subject's average mark, then overall average mark and pass/fail status.
    *   **Generate Student Report (`generate_student_report`)**:
        *   Gets a student.
        *   Calls `student.generate_report()` (polymorphic) and prints the returned string.

5.  **Data Operations:**
    *   **Save Data (`save_data`)**: Saves current `self.students` and `self.available_subjects` to `gradeforge_data.json`.
    *   **Load Data (`load_data`)**: Loads data from `gradeforge_data.json` on application start.
    *   **Export to CSV (`export_to_csv`)**:
        *   Prompts for a CSV filename.
        *   Writes a header row.
        *   Iterates through all students and their enrolled subjects/grades, writing one row per grade item (or one row per subject if no grades, or one row per student if no subjects).
        *   Includes student details, subject details, grade details, subject average, overall student average/GPA, and status.

## Technical Specifications

### System Requirements
-   Python 3.x (code uses f-strings, type hints, suggesting Python 3.6+).
-   Standard Python libraries: `json`, `csv`, `os`.

### Error Handling & Validation
-   `Student`, `Subject`, `Grade` constructors raise `ValueError` for invalid initial data (e.g., empty names/IDs, negative credit hours).
-   `GradeForge` methods handle user input errors (e.g., non-empty inputs, existing student IDs) by printing messages and returning.
-   `GradeForge.input_grades_for_subject()` validates score ranges and letter grades.
-   `GradeForge.save_data()` and `load_data()` use `try-except` for `IOError`, `FileNotFoundError`, `json.JSONDecodeError`, and other general exceptions, printing error messages.
-   Warnings are printed during `load_data` for individual records that cannot be processed due to `KeyError` or `ValueError`.

### Logging
-   The application uses `print()` statements for direct user feedback, warnings, and error messages rather than Python's `logging` module for structured, leveled logging or persistent log files.

## References

-   Martin, Robert C. "SOLID: Principles of Object Oriented Design." *Uncle Bob's Blog*, 2009. Available at [https://web.archive.org/web/20220310174829/https://blog.cleancoder.com/uncle-bob/2020/10/18/SOLID-Service-Locator.html](https://web.archive.org/web/20220310174829/https://blog.cleancoder.com/uncle-bob/2020/10/18/SOLID-Service-Locator.html) (Note: This is a common starting point; full definitions are often spread across various articles and talks).
-   Python Software Foundation. "The Python Tutorial." *Python Documentation*. Available at [https://docs.python.org/3/tutorial/](https://docs.python.org/3/tutorial/).
-   ECMA International. "ECMA-404: The JSON Data Interchange Format." *ECMA Standards*. Available at [https://www.ecma-international.org/publications-and-standards/standards/ecma-404/](https://www.ecma-international.org/publications-and-standards/standards/ecma-404/).
-   Gamma, Erich, et al. *Design Patterns: Elements of Reusable Object-Oriented Software*. Addison-Wesley, 1994.

## Appendix

### Key Data Files and Constants
-   `DATA_FILE = "gradeforge_data.json"`: Stores all persistent application data.
-   `GRADE_POINTS (dict)` in `student.py`: Defines mapping for letter grades to points for `CollegeStudent`.
-   `VALID_LETTER_GRADES (list)` in `student.py`: List of acceptable letter grades for `CollegeStudent`.

### Example Workflow (CLI Interaction)
1.  **Start `gradeforge.py`**. Data is loaded if `gradeforge_data.json` exists.
2.  User selects "1. Add New Student".
    *   Enters name "John Doe", ID "JD001", type "2" (College), major "History".
    *   System confirms: "Student John Doe (JD001) added successfully as CollegeStudent."
3.  User selects "7. List Available Subjects". (Assume HIST101 exists as a template).
4.  User selects "2. Assign Subject to Student".
    *   Enters student ID "JD001".
    *   Enters subject code "HIST101".
    *   Enters credit hours "3" for this student's enrollment.
    *   System confirms assignment.
5.  User selects "3. Input Grades for Subject".
    *   Enters student ID "JD001", subject code "HIST101".
    *   Enters description "Essay 1", letter grade "A".
    *   System confirms grade added.
    *   Enters description "Final Exam", letter grade "B+".
    *   System confirms grade added. Enters "done".
6.  User selects "4. View Student Performance Summary".
    *   Enters student ID "JD001".
    *   System displays GPA and academic status for John Doe.
7.  User selects "9. Save Data". System confirms data saved to `gradeforge_data.json`.
8.  User selects "0. Exit". System saves data again and exits.

---

*This documentation is maintained by the GradeForge development team. For support or inquiries, please contact the system administrator.* 
