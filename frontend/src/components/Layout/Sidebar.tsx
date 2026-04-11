import React from 'react';

export const Sidebar: React.FC = () => {
  return (
    <aside style={{ width: 240, borderRight: '1px solid #ddd', padding: 16 }}>
      <h3>课程导航</h3>
      <ul style={{ paddingLeft: 20 }}>
        <li>Course 1</li>
        <li>Course 2</li>
        <li>Course 3</li>
      </ul>
    </aside>
  );
};
