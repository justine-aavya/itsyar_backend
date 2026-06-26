from pydantic import BaseModel  #, Field, ConfigDict
from typing import List, Optional
from datetime import datetime



# --- Listing / Detail Schemas ---
class CourseItem(BaseModel):
    id: str
    title: str
    description: str
    category: str
    level: str
    imageUrl: Optional[str] = None
    instructor: str
    lessonCount: int
    duration: str
    tags: List[str]

class PaginationMeta(BaseModel):
    offset: int
    limit: int
    total: int
    hasMore: bool

class CourseListResponse(BaseModel):
    courses: List[CourseItem]
    pagination: PaginationMeta

class SearchMatchItem(BaseModel):
    id: str
    title: str
    description: str
    category: str
    level: str
    imageUrl: Optional[str] = None
    instructor: str
    matchField: str

class SearchResponse(BaseModel):
    results: List[SearchMatchItem]
    query: str
    totalMatches: int

class InstructorDetail(BaseModel):
    name: str
    avatarUrl: Optional[str] = None

class CourseDetailResponse(BaseModel):
    id: str
    title: str
    description: str
    category: str
    level: str
    lessonCount: int
    moduleCount: int
    duration: str
    imageUrl: Optional[str] = None
    instructor: InstructorDetail
    learningObjectives: List[str]
    courseIncludes: List[str]
    tags: List[str]

# --- Curriculum & Progress Schemas ---
class LessonCreateSchema(BaseModel):
    lessonId: str
    title: str
    duration: Optional[str] = None
    type: str
    questionCount: Optional[int] = None

class ModuleStructureSchema(BaseModel):
    moduleId: str
    moduleNumber: int
    title: str
    lessons: List[LessonCreateSchema]

class CurriculumResponse(BaseModel):
    courseId: str
    totalModules: int
    totalLessons: int
    modules: List[ModuleStructureSchema]

class EnrollmentStatusResponse(BaseModel):
    isEnrolled: bool
    enrolledAt: Optional[datetime] = None
    completionPercent: int
    lastAccessedLessonId: Optional[str] = None
    lastAccessedAt: Optional[datetime] = None

class EnrollmentSuccessResponse(BaseModel):
    status: str
    courseId: str
    userId: str
    enrolledAt: datetime
    message: str

# --- Progress Tracking ---
class LessonProgressStatus(BaseModel):
    lessonId: str
    title: str
    status: str

class ModuleProgressStatus(BaseModel):
    moduleId: str
    title: str
    status: str
    lessons: List[LessonProgressStatus]

class CourseProgressOverviewResponse(BaseModel):
    courseId: str
    overallPercent: int
    modules: List[ModuleProgressStatus]

# --- Lesson Content ---
class MaterialItem(BaseModel):
    materialId: str
    title: str
    type: str
    fileSize: str
    downloadUrl: str

class LessonContentResponse(BaseModel):
    lessonId: str
    title: str
    moduleTitle: str
    type: str
    videoUrl: Optional[str] = None
    videoDuration: Optional[str] = None
    summary: str
    materials: List[MaterialItem]

class LessonCompleteResponse(BaseModel):
    status: str
    lessonId: str
    moduleId: str
    courseId: str
    newCourseProgress: int
    newModuleProgress: int
    nextLessonId: Optional[str] = None
    message: str

# --- Assessments / Testing ---
class QuizOption(BaseModel):
    key: str
    text: str

class QuizQuestion(BaseModel):
    questionNumber: int
    questionText: str
    options: List[QuizOption]

class QuizAnswer(BaseModel):
    questionId: str
    answer: List[str]

class TestSubmissionRequest(BaseModel):
    answers: List[QuizAnswer]
    testId: Optional[str] = None
    timeElapsedSeconds: Optional[int] = None

class ModuleTestQuestionsResponse(BaseModel):
    testId: str
    moduleId: str
    moduleTitle: str
    coursePath: str
    totalQuestions: int
    timeLimitSeconds: int
    questions: List[QuizQuestion]

class TestSubmissionResponse(BaseModel):
    testId: str
    score: int
    totalQuestions: int
    percentage: int
    passed: bool
    passingThreshold: int
    timeElapsedSeconds: int
    submittedAt: datetime
    message: str
    moduleUnlocked: Optional[str] = None
    retakeAvailable: Optional[bool] = None

class HistoricalTestResultResponse(BaseModel):
    testId: str
    score: int
    totalQuestions: int
    percentage: int
    passed: bool
    attempts: int
    bestScore: int
    lastAttemptAt: datetime


# class LessonProgressRequest(BaseModel):
#     played_seconds: float = Field(alias="playedSeconds")
#     total_seconds: float = Field(alias="totalSeconds")
#     is_completed: Optional[bool] = Field(default=False, alias="isCompleted")

#     model_config = ConfigDict(populate_by_name=True)
