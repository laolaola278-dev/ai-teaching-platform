import { ThemeProvider, CssBaseline } from '@mui/material'
import { theme } from '../styles/theme'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import CoursesPage from './pages/CoursesPage'
import CourseDetailPage from './pages/CourseDetailPage'
import NotebookPage from './pages/NotebookPage'
import AlgorithmPlayground from './pages/AlgorithmPlayground'
import NotFoundPage from './pages/NotFoundPage'

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/courses" replace />} />
          <Route path="courses" element={<CoursesPage />} />
          <Route path="courses/:courseId" element={<CourseDetailPage />} />
          <Route path="courses/:courseId/chapters/:chapterId/notebooks/:notebookId" element={<NotebookPage />} />
          <Route path="algorithms" element={<AlgorithmPlayground />} />
          <Route path="*" element={<NotFoundPage />} />
        </Route>
      </Routes>
    </Router>
  )
}

export default App
