from grade import Grade

class Subject:
    """
    Represents a subject taken by a student.

    Attributes:
        name (str): The name of the subject (e.g., "Mathematics", "History").
        code (str): The unique code for the subject (e.g., "MATH101", "HIST202").
        credit_hours (int): The number of credit hours for the subject.
        grades (list[Grade]): A list of Grade objects for this subject.
    """
    def __init__(self, name: str, code: str, credit_hours: int = 0):
        """
        Initializes a new Subject instance.

        Args:
            name (str): The name of the subject.
            code (str): The unique code for the subject.
            credit_hours (int): The credit hours for the subject. Defaults to 0 (primarily for CollegeStudent use).
        """
        if not isinstance(name, str) or not name:
            raise ValueError("Subject name must be a non-empty string.")
        if not isinstance(code, str) or not code:
            raise ValueError("Subject code must be a non-empty string.")
        if not isinstance(credit_hours, int) or credit_hours < 0:
            raise ValueError("Credit hours must be a non-negative integer.")

        self.name = name
        self.code = code
        self.credit_hours = credit_hours
        self.grades: list[Grade] = []

    def add_grade(self, grade: Grade):
        """
        Adds a grade to the subject.

        Args:
            grade (Grade): The Grade object to add.
        """
        if not isinstance(grade, Grade):
            raise ValueError("Invalid grade object provided.")
        
        for existing_grade in self.grades:
            if existing_grade.description.lower() == grade.description.lower():
                raise ValueError(f"A grade with description '{grade.description}' already exists for this subject. Update not implemented.")

        self.grades.append(grade)

    def get_average_grade(self) -> float:
        """
        Calculates the average grade for this subject.
        For HighSchoolStudent, this is the average of numeric marks.
        For CollegeStudent, this is the average of grade points.

        Returns:
            float: The average grade/point. Returns 0.0 if there are no grades.
        """
        if not self.grades:
            return 0.0
        total_score = sum(g.score for g in self.grades)
        return total_score / len(self.grades)

    def __str__(self) -> str:
        """
        Returns a string representation of the subject.
        """
        return f"{self.name} ({self.code}, {self.credit_hours} credits) - Avg Score/Point: {self.get_average_grade():.2f}"

    def __repr__(self) -> str:
        """
        Returns a detailed string representation of the subject.
        """
        return f"Subject(name='{self.name}', code='{self.code}', credit_hours={self.credit_hours}, grades_count={len(self.grades)})" 