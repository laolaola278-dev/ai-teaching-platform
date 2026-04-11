import React from 'react';
import { Sidebar } from './Sidebar';

type Props = {
  children?: React.ReactNode;
};

export const MainLayout: React.FC<Props> = ({ children }) => {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: '240px 1fr', minHeight: '100vh' }}>
      <Sidebar />
      <main style={{ padding: 16 }}>{children}</main>
    </div>
  );
};
