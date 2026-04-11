import { useParams, Link } from 'react-router-dom'
import { FiArrowLeft, FiBook, FiClock, FiUsers, FiBarChart, FiChevronRight } from 'react-icons/fi'

// Mock data
const courseData = {
  fastbook: {
    id: 'fastbook',
    title: 'Fastbook - Deep Learning for Coders',
    description: 'Practical deep learning for coders using fastai and PyTorch. Learn by doing with real-world examples.',
    longDescription: 'This course takes you from the basics of deep learning to advanced concepts, all through practical examples. You\'ll learn how to build and train models for computer vision, natural language processing, and more.',
    instructor: 'Jeremy Howard & Sylvain Gugger',
    level: 'Intermediate',
    language: 'English',
    duration: '8 weeks',
    students: 1250,
    rating: 4.8,
    chapters: [
      { id: 'ch1', title: 'Introduction to Deep Learning', description: 'Get started with deep learning basics', duration: '2 hours', notebooks: 5, completed: true },
      { id: 'ch2', title: 'From Model to Production', description: 'Learn how to deploy models in production', duration: '3 hours', notebooks: 3, completed: true },
      { id: 'ch3', title: 'Ethics in AI', description: 'Understand the ethical implications of AI', duration: '1.5 hours', notebooks: 2, completed: false },
      { id: 'ch4', title: 'MNIST Basics', description: 'Build your first image classifier', duration: '4 hours', notebooks: 4, completed: false },
      { id: 'ch5', title: 'Pet Breeds Classification', description: 'Classify pet breeds using CNNs', duration: '5 hours', notebooks: 6, completed: false },
      { id: 'ch6', title: 'Multi-category Classification', description: 'Handle multiple categories in classification', duration: '3.5 hours', notebooks: 4, completed: false },
    ],
    prerequisites: ['Basic Python', 'High school math'],
    tools: ['Python', 'PyTorch', 'fastai', 'Jupyter'],
  },
  'llm-scratch': {
    id: 'llm-scratch',
    title: 'LLM from Scratch',
    description: 'Build Large Language Models from scratch with PyTorch. Understand transformers, attention, and training.',
    longDescription: 'This course dives deep into the architecture of modern large language models. You\'ll implement every component from scratch, including attention mechanisms, transformer blocks, and training loops.',
    instructor: 'AI Teaching Platform Team',
    level: 'Advanced',
    language: 'English',
    duration: '6 weeks',
    students: 890,
    rating: 4.9,
    chapters: [
      { id: 'llm-ch1', title: 'Core Transformer Implementation', description: 'Implement the transformer architecture', duration: '6 hours', notebooks: 8, completed: true },
      { id: 'llm-ch2', title: 'Alignment (SFT & RL)', description: 'Fine-tune models with supervised learning and reinforcement learning', duration: '8 hours', notebooks: 6, completed: false },
      { id: 'llm-ch3', title: 'Data Processing Pipeline', description: 'Process and clean training data', duration: '4 hours', notebooks: 7, completed: false },
      { id: 'llm-ch4', title: 'Kernel Optimizations', description: 'Optimize attention with custom kernels', duration: '5 hours', notebooks: 5, completed: false },
    ],
    prerequisites: ['PyTorch', 'Linear Algebra', 'Probability'],
    tools: ['PyTorch', 'Triton', 'Hugging Face', 'WandB'],
  },
}

export default function CourseDetailPage() {
  const { courseId } = useParams<{ courseId: string }>()
  const course = courseId ? courseData[courseId as keyof typeof courseData] : null

  if (!course) {
    return (
      <div className="text-center py-12">
        <h1 className="text-2xl font-bold text-gray-900">Course not found</h1>
        <p className="mt-2 text-gray-600">The requested course does not exist.</p>
        <Link to="/courses" className="mt-4 inline-flex items-center text-primary-600 hover:text-primary-700">
          <FiArrowLeft className="mr-2" />
          Back to Courses
        </Link>
      </div>
    )
  }

  const completedChapters = course.chapters.filter(ch => ch.completed).length
  const totalChapters = course.chapters.length
  const progress = totalChapters > 0 ? Math.round((completedChapters / totalChapters) * 100) : 0

  return (
    <div className="space-y-6">
      <div>
        <Link to="/courses" className="inline-flex items-center text-primary-600 hover:text-primary-700 mb-4">
          <FiArrowLeft className="mr-2" />
          Back to Courses
        </Link>
        
        <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-6">
          <div className="flex-1">
            <h1 className="text-3xl font-bold text-gray-900">{course.title}</h1>
            <p className="mt-2 text-gray-600">{course.description}</p>
            
            <div className="mt-4 flex flex-wrap gap-4">
              <div className="flex items-center space-x-2">
                <FiBook className="text-gray-400" />
                <span className="text-sm text-gray-700">{course.level}</span>
              </div>
              <div className="flex items-center space-x-2">
                <FiClock className="text-gray-400" />
                <span className="text-sm text-gray-700">{course.duration}</span>
              </div>
              <div className="flex items-center space-x-2">
                <FiUsers className="text-gray-400" />
                <span className="text-sm text-gray-700">{course.students.toLocaleString()} students</span>
              </div>
              <div className="flex items-center space-x-2">
                <FiBarChart className="text-gray-400" />
                <span className="text-sm text-gray-700">Rating: {course.rating}/5.0</span>
              </div>
            </div>
          </div>
          
          <div className="lg:w-64">
            <div className="card">
              <h3 className="font-semibold text-gray-900">Course Progress</h3>
              <div className="mt-4">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm text-gray-700">Overall Progress</span>
                  <span className="text-sm font-semibold text-gray-900">{progress}%</span>
                </div>
                <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-green-500 rounded-full"
                    style={{ width: `${progress}%` }}
                  />
                </div>
                <div className="mt-2 text-sm text-gray-600">
                  {completedChapters} of {totalChapters} chapters completed
                </div>
              </div>
              
              <button className="w-full mt-6 btn-primary">
                {progress === 0 ? 'Start Course' : progress === 100 ? 'Review Course' : 'Continue Learning'}
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="card">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Course Content</h2>
            <div className="space-y-3">
              {course.chapters.map((chapter, index) => (
                <Link
                  key={chapter.id}
                  to={`/courses/${course.id}/chapters/${chapter.id}/notebooks/notebook-1`}
                  className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:border-primary-300 hover:bg-primary-50 transition-colors group"
                >
                  <div className="flex items-center space-x-4">
                    <div className="flex items-center justify-center w-8 h-8 rounded-full bg-gray-100 group-hover:bg-primary-100">
                      <span className="text-sm font-medium text-gray-700 group-hover:text-primary-700">
                        {index + 1}
                      </span>
                    </div>
                    <div>
                      <h3 className="font-medium text-gray-900 group-hover:text-primary-700">
                        {chapter.title}
                      </h3>
                      <p className="text-sm text-gray-600">{chapter.description}</p>
                      <div className="mt-1 flex items-center space-x-4 text-xs text-gray-500">
                        <span>{chapter.duration}</span>
                        <span>•</span>
                        <span>{chapter.notebooks} notebooks</span>
                        {chapter.completed && (
                          <>
                            <span>•</span>
                            <span className="text-green-600 font-medium">Completed</span>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                  <FiChevronRight className="text-gray-400 group-hover:text-primary-500" />
                </Link>
              ))}
            </div>
          </div>

          <div className="card">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">About This Course</h2>
            <p className="text-gray-700">{course.longDescription}</p>
            
            <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="font-medium text-gray-900 mb-2">Prerequisites</h3>
                <ul className="space-y-1">
                  {course.prerequisites.map((prereq, idx) => (
                    <li key={idx} className="flex items-center text-gray-700">
                      <span className="w-2 h-2 bg-primary-500 rounded-full mr-2"></span>
                      {prereq}
                    </li>
                  ))}
                </ul>
              </div>
              <div>
                <h3 className="font-medium text-gray-900 mb-2">Tools & Technologies</h3>
                <div className="flex flex-wrap gap-2">
                  {course.tools.map((tool, idx) => (
                    <span
                      key={idx}
                      className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm"
                    >
                      {tool}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="space-y-6">
          <div className="card">
            <h3 className="font-semibold text-gray-900 mb-4">Instructor</h3>
            <div className="flex items-center space-x-3">
              <div className="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center">
                <FiBook className="text-primary-600 text-xl" />
              </div>
              <div>
                <div className="font-medium text-gray-900">{course.instructor}</div>
                <div className="text-sm text-gray-600">Course Instructor</div>
              </div>
            </div>
            <p className="mt-4 text-sm text-gray-700">
              Experienced AI researcher and educator with years of experience in deep learning.
            </p>
          </div>

          <div className="card">
            <h3 className="font-semibold text-gray-900 mb-4">Course Stats</h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-700">Total Chapters</span>
                <span className="font-medium text-gray-900">{totalChapters}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-700">Total Notebooks</span>
                <span className="font-medium text-gray-900">
                  {course.chapters.reduce((sum, ch) => sum + ch.notebooks, 0)}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-700">Total Duration</span>
                <span className="font-medium text-gray-900">
                  {course.chapters.reduce((sum, ch) => {
                    const hours = parseFloat(ch.duration.split(' ')[0])
                    return sum + hours
                  }, 0).toFixed(1)} hours
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-700">Language</span>
                <span className="font-medium text-gray-900">{course.language}</span>
              </div>
            </div>
          </div>

          <div className="card">
            <h3 className="font-semibold text-gray-900 mb-4">Certificate</h3>
            <p className="text-sm text-gray-700 mb-4">
              Earn a certificate upon completion of all chapters and assessments.
            </p>
            <div className="p-4 border border-gray-200 rounded-lg bg-gray-50">
              <div className="text-center">
                <div className="text-lg font-bold text-gray-900">AI Teaching Platform</div>
                <div className="text-sm text-gray-600 mt-1">Certificate of Completion</div>
              </div>
            </div>
            <button className="w-full mt-4 btn-secondary">
              View Certificate Requirements
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}