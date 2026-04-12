import { ThemeProvider, CssBaseline } from '@mui/material'
import 'katex/dist/katex.min.css'
import { theme } from './styles/theme'
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom'
import Layout from './components/Layout'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import { Login } from './pages/Login'
import { Register } from './pages/Register'
import CoursesPage from './pages/CoursesPage'
import CourseDetailPage from './pages/CourseDetailPage'
import NotebookPage from './pages/NotebookPage'
import AlgorithmPlayground from './pages/AlgorithmPlayground'
import NotFoundPage from './pages/NotFoundPage'

function PrivateRoute({ children }: { children: JSX.Element }) {
  const { user } = useAuth()
  const location = useLocation()
  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }
  return children
}

function App() {
  return (
    <AuthProvider>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Router>
          <Routes>
            <Route path="/" element={<Layout />}>
              <Route index element={<Navigate to="/courses" replace />} />
              <Route path="login" element={<Login />} />
              <Route path="register" element={<Register />} />
              <Route path="courses" element={<PrivateRoute><CoursesPage /></PrivateRoute>} />
              <Route path="courses/:courseId" element={<PrivateRoute><CourseDetailPage /></PrivateRoute>} />
              <Route path="courses/:courseId/chapters/:chapterId/notebooks/:notebookId" element={<PrivateRoute><NotebookPage /></PrivateRoute>} />
              <Route path="algorithms" element={<PrivateRoute><AlgorithmPlayground /></PrivateRoute>} />
              <Route path="*" element={<NotFoundPage />} />
            </Route>
          </Routes>
        </Router>
      </ThemeProvider>
    </AuthProvider>
  )
}

export default App
