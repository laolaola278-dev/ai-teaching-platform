import React from 'react';
import { MainLayout } from '../components/Layout/MainLayout';
import { MarkdownViewer } from '../components/Editor/MarkdownViewer';

export const CoursePage: React.FC = () => {
  const markdown = `# 课程概览\nThis is a placeholder course description.`;
  return (
    <MainLayout>
      <h2>Course Page</h2>
      <MarkdownViewer content={markdown} />
    </MainLayout>
  );
};
