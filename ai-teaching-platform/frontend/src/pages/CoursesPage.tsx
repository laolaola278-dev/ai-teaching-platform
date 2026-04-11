import { Link } from 'react-router-dom'
import { FiBook, FiCpu, FiUsers, FiClock, FiBarChart } from 'react-icons/fi'

// Mock data
const courses = [
  {
    id: 'fastbook',
    title: 'Fastbook - Deep Learning for Coders',
    description: 'Practical deep learning for coders using fastai and PyTorch. Learn by doing with real-world examples.',
    icon: FiBook,
    color: 'bg-blue-500',
    stats: {
      chapters: 20,
      notebooks: 85,
      students: 1250,
      duration: '8 weeks',
    },
    progress: 65,
  },
  {
    id: 'llm-scratch',
    title: 'LLM from Scratch',
    description: 'Build Large Language Models from scratch with PyTorch. Understand transformers, attention, and training.',
    icon: FiCpu,
    color: 'bg-purple-500',
    stats: {
      chapters: 6,
      notebooks: 42,
      students: 890,
      duration: '6 weeks',
    },
    progress: 30,
  },
  {
    id: 'ml-fundamentals',
    title: 'Machine Learning Fundamentals',
    description: 'Core concepts of machine learning including regression, classification, and clustering.',
    icon: FiBarChart,
    color: 'bg-green-500',
    stats: {
      chapters: 12,
      notebooks: 50,
      students: 2100,
      duration: '10 weeks',
    },
    progress: 100,
  },
  {
    id: 'dl-advanced',
    title: 'Advanced Deep Learning',
    description: 'Advanced topics including GANs, reinforcement learning, and model optimization.',
    icon: FiCpu,
    color: 'bg-red-500',
    stats: {
      chapters: 15,
      notebooks: 60,
      students: 750,
      duration: '12 weeks',
    },
    progress: 0,
  },
]

export default function CoursesPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Courses</h1>
        <p className="mt-2 text-gray-600">
          Browse and explore our collection of AI and machine learning courses.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {courses.map(course => (
          <Link
            key={course.id}
            to={`/courses/${course.id}`}
            className="card hover:shadow-lg transition-shadow duration-300"
          >
            <div className="flex items-start justify-between">
              <div className={`${course.color} w-12 h-12 rounded-lg flex items-center justify-center`}>
                <course.icon className="text-white text-xl" />
              </div>
              <div className="flex items-center space-x-2">
                <span className="text-sm font-medium text-gray-700">
                  {course.progress}%
                </span>
                <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-green-500 rounded-full"
                    style={{ width: `${course.progress}%` }}
                  />
                </div>
              </div>
            </div>

            <h3 className="mt-4 text-xl font-semibold text-gray-900">
              {course.title}
            </h3>
            <p className="mt-2 text-gray-600 line-clamp-2">
              {course.description}
            </p>

            <div className="mt-6 grid grid-cols-2 gap-4">
              <div className="flex items-center space-x-2">
                <FiBook className="text-gray-400" />
                <span className="text-sm text-gray-700">
                  {course.stats.chapters} chapters
                </span>
              </div>
              <div className="flex items-center space-x-2">
                <FiUsers className="text-gray-400" />
                <span className="text-sm text-gray-700">
                  {course.stats.students} students
                </span>
              </div>
              <div className="flex items-center space-x-2">
                <FiClock className="text-gray-400" />
                <span className="text-sm text-gray-700">
                  {course.stats.duration}
                </span>
              </div>
              <div className="flex items-center space-x-2">
                <FiBarChart className="text-gray-400" />
                <span className="text-sm text-gray-700">
                  {course.stats.notebooks} notebooks
                </span>
              </div>
            </div>

            <div className="mt-6">
              <button className="w-full btn-primary">
                {course.progress === 0 ? 'Start Course' : 'Continue Learning'}
              </button>
            </div>
          </Link>
        ))}
      </div>

      <div className="card">
        <h2 className="text-xl font-semibold text-gray-900">Learning Progress</h2>
        <p className="mt-2 text-gray-600">
          Track your progress across all courses and notebooks.
        </p>
        
        <div className="mt-6 space-y-4">
          {courses.map(course => (
            <div key={course.id} className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className={`${course.color} w-8 h-8 rounded flex items-center justify-center`}>
                  <course.icon className="text-white" size={16} />
                </div>
                <span className="font-medium text-gray-900">{course.title}</span>
              </div>
              <div className="flex items-center space-x-4">
                <div className="w-48 h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-green-500 rounded-full"
                    style={{ width: `${course.progress}%` }}
                  />
                </div>
                <span className="text-sm font-medium text-gray-700 w-10">
                  {course.progress}%
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}