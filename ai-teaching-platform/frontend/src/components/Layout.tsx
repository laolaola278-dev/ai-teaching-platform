import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'
import Header from './Header'

export default function Layout() {
  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <div className="flex flex-col flex-1 overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
        <footer className="bg-white border-t border-gray-200 px-6 py-4 text-sm text-gray-500">
          <div className="flex justify-between items-center">
            <span>AI Teaching Platform © 2024</span>
            <span>v0.1.0</span>
          </div>
        </footer>
      </div>
    </div>
  )
}