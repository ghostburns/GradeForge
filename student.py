from subject import Subject
from grade import Grade

# Grade point mapping for CollegeStudent
GRADE_POINTS = {
    "A+": 4.0, "A": 4.0, "A-": 3.75,
    "B+": 3.5, "B": 3.0, "B-": 2.75,
    "C+": 2.5, "C": 2.0, "C-": 1.75,
    "D": 1.5, "F": 0.0
}
VALID_LETTER_GRADES = list(GRADE_POINTS.keys())

class Student:
    """
    Represents a student in the grade management system.

    Attributes:
        name (str): The name of the student.
        student_id (str): The unique ID of the student.
        enrolled_subjects (dict[str, Subject]): A dictionary of subjects the student is enrolled in,
                                                 keyed by subject code.
    """
    def __init__(self, name: str, student_id: str):
        """
        Initializes a new Student instance.

        Args:
            name (str): The name of the student.
            student_id (str): The unique ID of the student.
        """
        if not isinstance(name, str) or not name:
            raise ValueError("Student name must be a non-empty string.")
        if not isinstance(student_id, str) or not student_id:
            raise ValueError("Student ID must be a non-empty string.")

        self.name = name
        self.student_id = student_id
        self.enrolled_subjects: dict[str, Subject] = {}

    def enroll_subject(self, subject: Subject):
        """
        Enrolls the student in a subject.

        Args:
            subject (Subject): The Subject object to enroll in.
        
        Raises:
            ValueError: If the subject is already enrolled or not a valid Subject instance.
        """
        if not isinstance(subject, Subject):
            raise ValueError("Invalid subject object provided.")
        if subject.code in self.enrolled_subjects:
            raise ValueError(f"Student already enrolled in {subject.name} ({subject.code}).")
        self.enrolled_subjects[subject.code] = subject

    def add_grade_to_subject(self, subject_code: str, grade: Grade):
        """
        Adds a grade to a specific subject for this student.
        This method is used by HighSchoolStudent directly.
        CollegeStudent uses this after converting letter grade to a Grade object.

        Args:
            subject_code (str): The code of the subject to add the grade to.
            grade (Grade): The Grade object to add.
        
        Raises:
            ValueError: If the subject code is not found or grade is invalid.
        """
        if subject_code not in self.enrolled_subjects:
            raise ValueError(f"Subject with code {subject_code} not found for this student.")
        if not isinstance(grade, Grade):
            raise ValueError("Invalid grade object provided.")
        self.enrolled_subjects[subject_code].add_grade(grade)

    def get_subject_average(self, subject_code: str) -> float | None:
        """
        Gets the average grade for a specific subject.
        For HighSchoolStudent, this is average of numeric marks.
        For CollegeStudent, this is average of grade points.

        Args:
            subject_code (str): The code of the subject.

        Returns:
            float | None: The average grade/point for the subject, or None if subject not found.
        """
        subject = self.enrolled_subjects.get(subject_code)
        if subject:
            return subject.get_average_grade()
        return None

    def get_overall_average(self) -> float:
        """
        Calculates the overall average grade for the student across all subjects.
        For HighSchoolStudent, this is the average of subject numeric averages.
        For CollegeStudent, this is overridden to return GPA.

        Returns:
            float: The overall average grade. Returns 0.0 if no subjects or no grades.
        """
        if not self.enrolled_subjects:
            return 0.0
        
        total_average_sum = 0
        count = 0
        for subject in self.enrolled_subjects.values():
            if subject.grades: 
                total_average_sum += subject.get_average_grade()
                count += 1
        
        if count == 0: 
            return 0.0
        return total_average_sum / count

    def get_pass_fail_status(self, threshold: float = 50.0) -> str:
        """
        Determines the pass/fail status of the student.
        For HighSchoolStudent, based on overall average numeric score (threshold 50.0).
        For CollegeStudent, this is overridden for GPA-based status.

        Args:
            threshold (float): The passing threshold. Defaults to 50.0 for numeric scores.

        Returns:
            str: "Pass" or "Fail" (for HS), or specific status for College.
        """
        overall_avg = self.get_overall_average()
        return "Pass" if overall_avg >= threshold else "Fail"

    def generate_report(self) -> str:
        """
        Generates a performance report for the student.
        Suitable for HighSchoolStudent. CollegeStudent overrides this.

        Returns:
            str: A string containing the student's report.
        """
        report = f"Student Report\n"
        report += f"------------------------------------\n"
        report += f"Name: {self.name}\n"
        report += f"ID: {self.student_id}\n"
        report += f"Type: {self.__class__.__name__}\n"
        report += f"------------------------------------\n"
        report += "Subjects Enrolled:\n"
        if not self.enrolled_subjects:
            report += "  No subjects enrolled.\n"
        else:
            for subject_code, subject in self.enrolled_subjects.items():
                avg = subject.get_average_grade()
                report += f"  - {subject.name} ({subject.code}): Average = {avg:.2f}\n"
                if subject.grades:
                    for grade_item in subject.grades:
                        report += f"    - {str(grade_item)}\n" # Uses Grade.__str__
                else:
                    report += f"    - No grades recorded.\n"
        report += f"------------------------------------\n"
        report += f"Overall Average: {self.get_overall_average():.2f}\n"
        report += f"Status: {self.get_pass_fail_status()}\n"
        report += f"------------------------------------\n"
        return report

    def __str__(self) -> str:
        """
        Returns a string representation of the student.
        """
        return f"Student Name: {self.name}, ID: {self.student_id}, Overall Avg: {self.get_overall_average():.2f}"

    def __repr__(self) -> str:
        """
        Returns a detailed string representation of the student.
        """
        return f"Student(name='{self.name}', student_id='{self.student_id}', subjects_count={len(self.enrolled_subjects)})"


class HighSchoolStudent(Student):
    """
    Represents a high school student. Uses numeric grades (0-100).
    Pass threshold is 50% on the overall average.
    Inherits most calculation and reporting logic from the base Student class.
    """
    def __init__(self, name: str, student_id: str):
        super().__init__(name, student_id)
        # High school specific attributes can be added here if needed

    # HighSchoolStudent uses the base Student methods for:
    # - add_grade_to_subject (expects Grade object with numeric score)
    # - get_subject_average (calculates average of numeric scores)
    # - get_overall_average (calculates average of subject numeric averages)
    # - get_pass_fail_status (uses 50% threshold on overall numeric average)
    # - generate_report (displays numeric scores and averages)


class CollegeStudent(Student):
    """
    Represents a college student. Uses letter grades and GPA.
    Subject failures are determined by 'F' grades.
    GPA is calculated based on grade points and credit hours.
    """
    def __init__(self, name: str, student_id: str, major: str = "Undeclared"):
        super().__init__(name, student_id)
        self.major = major

    def get_gpa(self) -> float:
        """
        Calculates the Grade Point Average (GPA) for the college student.
        GPA = sum(grade_point_for_subject * credit_hours_for_subject) / total_credit_hours_taken.
        The grade_point_for_subject is the average of grade points if multiple assignments exist.
        
        Returns:
            float: The calculated GPA. Returns 0.0 if no subjects with grades or no credit hours.
        """
        total_weighted_points = 0.0
        total_credit_hours_attempted = 0

        if not self.enrolled_subjects:
            return 0.0

        for subject in self.enrolled_subjects.values():
            if subject.grades: # Only consider subjects for which grades have been entered
                # Subject.get_average_grade() for CollegeStudent will average the grade.score values,
                # which are the grade points for each assignment/exam in that subject.
                subject_average_points = subject.get_average_grade()
                total_weighted_points += subject_average_points * subject.credit_hours
                total_credit_hours_attempted += subject.credit_hours
        
        if total_credit_hours_attempted == 0:
            return 0.0
        
        return total_weighted_points / total_credit_hours_attempted

    def check_for_f_grades(self) -> bool:
        """
        Checks if the student has received an 'F' grade in any subject.

        Returns:
            bool: True if an 'F' grade is found, False otherwise.
        """
        for subject in self.enrolled_subjects.values():
            for grade_item in subject.grades:
                if grade_item.letter_grade == "F":
                    return True
        return False

    def get_overall_average(self) -> float:
        """Overrides base method to return GPA for CollegeStudent."""
        return self.get_gpa()

    def get_pass_fail_status(self, gpa_threshold_good_standing: float = 2.0) -> str:
        """
        Determines the academic standing for a CollegeStudent.
        Considers 'F' grades and GPA against a threshold.

        Args:
            gpa_threshold_good_standing (float): GPA threshold for good standing. Defaults to 2.0.

        Returns:
            str: Academic standing status (e.g., "Good Standing", "At Risk").
        """
        gpa = self.get_gpa()
        has_f = self.check_for_f_grades()

        if has_f:
            return "At Risk (Failing one or more courses)"
        if gpa < gpa_threshold_good_standing:
            return f"At Risk (GPA below {gpa_threshold_good_standing:.1f})"
        return "Good Standing"

    def generate_report(self) -> str:
        """
        Generates a detailed performance report for the CollegeStudent.
        Displays letter grades, grade points, credit hours, GPA, and F grade status.

        Returns:
            str: A string containing the student's report.
        """
        report = f"Student Report\n"
        report += f"------------------------------------\n"
        report += f"Name: {self.name}\n"
        report += f"ID: {self.student_id}\n"
        report += f"Type: {self.__class__.__name__}\n"
        report += f"Major: {self.major}\n"
        report += f"------------------------------------\n"
        report += "Subjects Enrolled:\n"
        if not self.enrolled_subjects:
            report += "  No subjects enrolled.\n"
        else:
            for subject_code, subject in self.enrolled_subjects.items():
                report += f"  - {subject.name} ({subject.code}) - {subject.credit_hours} Credit Hours\n"
                if subject.grades:
                    for grade_item in subject.grades:
                        # Grade.__str__ will format this nicely with letter grade and points
                        report += f"    - {str(grade_item)}\n"
                    # Display average grade points for the subject
                    report += f"    Subject Average Points: {subject.get_average_grade():.2f}\n"
                else:
                    report += f"    - No grades recorded for this subject.\n"
        report += f"------------------------------------\n"
        report += f"Overall GPA: {self.get_gpa():.2f}\n"
        # Use the specific pass/fail status method for CollegeStudent
        report += f"Academic Status: {self.get_pass_fail_status()}\n" 
        if self.check_for_f_grades():
            report += f"Note: Student has received an 'F' in one or more courses.\n"
        report += f"------------------------------------\n"
        return report

    def __str__(self) -> str:
        return f"College Student: {self.name}, ID: {self.student_id}, Major: {self.major}, GPA: {self.get_gpa():.2f}"

    def __repr__(self) -> str:
        return f"CollegeStudent(name='{self.name}', student_id='{self.student_id}', major='{self.major}', subjects_count={len(self.enrolled_subjects)})" 