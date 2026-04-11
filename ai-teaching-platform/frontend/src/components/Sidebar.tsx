import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { 
  FiBook, 
  FiCpu, 
  FiHome, 
  FiChevronDown, 
  FiChevronRight,
  FiFileText,
  FiFolder
} from 'react-icons/fi'

// Mock data for development
const mockCourses = [
  {
    id: 'fastbook',
    title: 'Fastbook - Deep Learning',
    icon: FiBook,
    chapters: [
      { id: 'ch1', title: 'Introduction', notebooks: 5 },
      { id: 'ch2', title: 'Production', notebooks: 3 },
      { id: 'ch3', title: 'Ethics', notebooks: 2 },
      { id: 'ch4', title: 'MNIST Basics', notebooks: 4 },
    ],
  },
  {
    id: 'llm-scratch',
    title: 'LLM from Scratch',
    icon: FiCpu,
    chapters: [
      { id: 'llm-ch1', title: 'Core Transformer', notebooks: 8 },
      { id: 'llm-ch2', title: 'Alignment', notebooks: 6 },
      { id: 'llm-ch3', title: 'Data Processing', notebooks: 7 },
    ],
  },
]

const navItems = [
  { id: 'home', label: 'Dashboard', icon: FiHome, path: '/' },
  { id: 'courses', label: 'Courses', icon: FiBook, path: '/courses' },
  { id: 'algorithms', label: 'Algorithm Playground', icon: FiCpu, path: '/algorithms' },
]

export default function Sidebar() {
  const location = useLocation()
  const [expandedCourses, setExpandedCourses] = useState<string[]>(['fastbook'])
  const [expandedChapters, setExpandedChapters] = useState<string[]>([])

  const toggleCourse = (courseId: string) => {
    setExpandedCourses(prev =>
      prev.includes(courseId)
        ? prev.filter(id => id !== courseId)
        : [...prev, courseId]
    )
  }

  const toggleChapter = (chapterId: string) => {
    setExpandedChapters(prev =>
      prev.includes(chapterId)
        ? prev.filter(id => id !== chapterId)
        : [...prev, chapterId]
    )
  }

  const isActive = (path: string) => {
    if (path === '/') {
      return location.pathname === '/'
    }
    return location.pathname.startsWith(path)
  }

  return (
    <div className="flex flex-col w-64 bg-white border-r border-gray-200">
      <div className="p-6">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center">
            <FiCpu className="text-white text-xl" />
          </div>
          <div>
            <div className="font-bold text-gray-900">AI Teaching</div>
            <div className="text-xs text-gray-500">Platform</div>
          </div>
        </div>
      </div>
      
      <nav className="flex-1 px-4 pb-4 overflow-y-auto">
        <div className="space-y-2">
          {navItems.map(item => (
            <Link
              key={item.id}
              to={item.path}
              className={`flex items-center px-4 py-3 rounded-lg transition-colors ${
                isActive(item.path)
                  ? 'bg-primary-50 text-primary-700'
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              <item.icon className="mr-3" size={20} />
              <span className="font-medium">{item.label}</span>
            </Link>
          ))}
        </div>

        <div className="mt-8">
          <div className="px-4 mb-2 text-xs font-semibold text-gray-500 uppercase tracking-wider">
            Courses
          </div>
          
          <div className="space-y-1">
            {mockCourses.map(course => (
              <div key={course.id} className="rounded-lg">
                <button
                  onClick={() => toggleCourse(course.id)}
                  className={`flex items-center justify-between w-full px-4 py-3 rounded-lg text-left transition-colors ${
                    expandedCourses.includes(course.id)
                      ? 'bg-gray-100 text-gray-900'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  <div className="flex items-center">
                    <course.icon className="mr-3" size={18} />
                    <span className="font-medium truncate">{course.title}</span>
                  </div>
                  {expandedCourses.includes(course.id) ? (
                    <FiChevronDown size={16} />
                  ) : (
                    <FiChevronRight size={16} />
                  )}
                </button>
                
                {expandedCourses.includes(course.id) && (
                  <div className="ml-8 mt-1 space-y-1">
                    {course.chapters.map(chapter => (
                      <div key={chapter.id} className="rounded-lg">
                        <button
                          onClick={() => toggleChapter(chapter.id)}
                          className={`flex items-center justify-between w-full px-3 py-2 rounded-lg text-left transition-colors ${
                            expandedChapters.includes(chapter.id)
                              ? 'bg-gray-50 text-gray-900'
                              : 'text-gray-600 hover:bg-gray-50'
                          }`}
                        >
                          <div className="flex items-center">
                            <FiFolder className="mr-2" size={16} />
                            <span className="truncate">{chapter.title}</span>
                          </div>
                          <div className="flex items-center space-x-2">
                            <span className="text-xs text-gray-500">
                              {chapter.notebooks}
                            </span>
                            {expandedChapters.includes(chapter.id) ? (
                              <FiChevronDown size={14} />
                            ) : (
                              <FiChevronRight size={14} />
                            )}
                          </div>
                        </button>
                        
                        {expandedChapters.includes(chapter.id) && (
                          <div className="ml-6 mt-1 space-y-1">
                            {[...Array(chapter.notebooks)].map((_, i) => (
                              <Link
                                key={i}
                                to={`/courses/${course.id}/chapters/${chapter.id}/notebooks/notebook-${i + 1}`}
                                className="flex items-center px-3 py-2 text-sm text-gray-600 hover:bg-gray-50 rounded-lg"
                              >
                                <FiFileText className="mr-2" size={14} />
                                <span className="truncate">
                                  Notebook {i + 1}
                                </span>
                              </Link>
                            ))}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </nav>

      <div className="p-4 border-t border-gray-200">
        <div className="flex items-center space-x-3 px-3 py-2 bg-gray-50 rounded-lg">
          <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
            <FiUser className="text-primary-600" size={16} />
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-sm font-medium truncate">John Doe</div>
            <div className="text-xs text-gray-500 truncate">john@example.com</div>
          </div>
        </div>
      </div>
    </div>
  )
}