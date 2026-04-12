import { useParams, Link } from 'react-router-dom'
import { FiArrowLeft, FiBook, FiClock, FiUsers, FiBarChart, FiChevronRight } from 'react-icons/fi'
import React, { useEffect, useState } from 'react'
import Alert from '@mui/material/Alert'
import IconButton from '@mui/material/IconButton'
import RefreshIcon from '@mui/icons-material/Refresh'
import CircularProgress from '@mui/material/CircularProgress'
import Typography from '@mui/material/Typography'
import Button from '@mui/material/Button'
import { MarkdownViewer } from '../components/Editor/MarkdownViewer'

type Chapter = { id: string; title: string; description?: string; duration?: string; notebooks?: number; completed?: boolean }
type CourseAPI = {
  id: string; title: string; description?: string; longDescription?: string; instructor?: string; level?: string; language?: string; duration?: string; students?: number; rating?: number; chapters?: Chapter[]; prerequisites?: string[]; tools?: string[]
}

export default function CourseDetailPage() {
  const { courseId } = useParams<{ courseId: string }>()
  const [course, setCourse] = useState<CourseAPI | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const fetchCourse = () => {
    setLoading(true)
    setError(null)
    if (!courseId) {
      setLoading(false)
      return
    }
    fetch(`/api/v1/courses/${courseId}`)
      .then(r => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`)
        return r.json()
      })
      .then((data: CourseAPI) => {
        setCourse(data)
        setLoading(false)
      })
      .catch(() => {
        setError('Failed to load course data.')
        setLoading(false)
      })
  }

  useEffect(() => {
    fetchCourse()
  }, [courseId])

  if (loading) {
    return (
      <div className="text-center py-12" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <CircularProgress color="primary" />
        <Typography variant="body1" style={{ marginTop: 8 }}>Loading course...</Typography>
      </div>
    )
  }
  if (error) {
    return (
      <div className="text-center py-12">
        <Alert severity="error" action={
          <IconButton color="inherit" size="small" onClick={() => fetchCourse()} aria-label="retry">
            <RefreshIcon fontSize="inherit" />
          </IconButton>
        }>{error}</Alert>
      </div>
    )
  }
  if (!course) {
    return (
      <div className="text-center py-12" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <Typography variant="h5">No course data available</Typography>
        <Button variant="contained" color="primary" startIcon={<RefreshIcon />} onClick={() => fetchCourse()} sx={{ mt: 2 }}>
          Reload
        </Button>
        <Button variant="text" color="primary" href="/courses" sx={{ mt: 1 }}>
          Back to Courses
        </Button>
      </div>
    )
  }

  const chapters = course?.chapters ?? []
  const completedChapters = chapters.filter(ch => ch.completed).length
  const totalChapters = chapters.length
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
            <h1 className="text-3xl font-bold text-gray-900">{course?.title ?? ''}</h1>
            <p className="mt-2 text-gray-600">{course?.description ?? ''}</p>
            
            <div className="mt-4 flex flex-wrap gap-4">
              <div className="flex items-center space-x-2">
                <FiBook className="text-gray-400" />
                <span className="text-sm text-gray-700">{course?.level ?? ''}</span>
              </div>
              <div className="flex items-center space-x-2">
                <FiClock className="text-gray-400" />
                <span className="text-sm text-gray-700">{course?.duration ?? ''}</span>
              </div>
              <div className="flex items-center space-x-2">
                <FiUsers className="text-gray-400" />
                <span className="text-sm text-gray-700">{(course?.students ?? 0).toLocaleString()} students</span>
              </div>
              <div className="flex items-center space-x-2">
                <FiBarChart className="text-gray-400" />
                <span className="text-sm text-gray-700">Rating: {course?.rating ?? 0}/5.0</span>
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
            {chapters.map((chapter, index) => (
                <Link
                  key={chapter.id}
                  to={`/courses/${course?.id}/chapters/${chapter.id}/notebooks/notebook-1`}
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
              <p className="text-gray-700">{course.longDescription ?? ''}</p>
            
            <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="font-medium text-gray-900 mb-2">Prerequisites</h3>
                <ul className="space-y-1">
              {(course?.prerequisites ?? []).map((prereq, idx) => (
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
                  {(course?.tools ?? []).map((tool, idx) => (
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
                <div className="font-medium text-gray-900">{course?.instructor ?? ''}</div>
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
                    {chapters.reduce((sum, ch) => sum + (ch.notebooks ?? 0), 0)}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-700">Total Duration</span>
                  <span className="font-medium text-gray-900">
                    {chapters.reduce((sum, ch) => {
                      const hours = parseFloat((ch.duration ?? '').split(' ')[0] || '0')
                      return sum + hours
                    }, 0).toFixed(1)} hours
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-700">Language</span>
                  <span className="font-medium text-gray-900">{course?.language ?? ''}</span>
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
