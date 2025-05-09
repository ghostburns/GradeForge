class Grade:
    """
    Represents a single grade entry for a subject.

    Attributes:
        description (str): The description of the grade (e.g., "Midterm Exam", "Assignment 1").
        score (float): The numeric score or grade point. For HighSchoolStudent, this is the mark (0-100).
                       For CollegeStudent, this is the grade point (e.g., 0.0-4.0).
        letter_grade (str | None): The letter grade (e.g., "A+", "B-"), applicable for CollegeStudent.
    """
    def __init__(self, description: str, score: float, letter_grade: str | None = None):
        """
        Initializes a new Grade instance.

        Args:
            description (str): The description of the grade.
            score (float): The numeric score or grade point.
            letter_grade (str | None, optional): The letter grade. Defaults to None.
        """
        if not isinstance(description, str) or not description:
            raise ValueError("Description must be a non-empty string.")
        if not isinstance(score, (int, float)):
            raise ValueError("Score/Grade Point must be a number.")
        # Score range validation (e.g., 0-100 for HS, 0-4 for College points)
        # should be handled by the calling code before creating a Grade object,
        # as the valid range depends on the context (HS numeric vs. College point).

        self.description = description
        self.score = float(score)
        self.letter_grade = letter_grade

    def __str__(self) -> str:
        """
        Returns a string representation of the grade.
        """
        if self.letter_grade:
            return f"{self.description}: {self.letter_grade} ({self.score:.2f} points)"
        return f"{self.description}: {self.score:.2f}"

    def __repr__(self) -> str:
        """
        Returns a detailed string representation of the grade, useful for debugging.
        """
        return f"Grade(description='{self.description}', score={self.score}, letter_grade='{self.letter_grade}')" 